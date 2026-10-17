import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, dirname, join, resolve } from 'node:path'
import { createInterface } from 'node:readline'
import { test } from 'node:test'
import { mountWritingPlugin, resolveServerConfig } from '../adapter.js'

test('mounts MCP before registering scoped literal generation guidance', async () => {
  const sections = [], events = []
  const ctx = { systemPrompt: { section: value => { sections.push(value); events.push('section') } } }
  await mountWritingPlugin(ctx, {serverName: 'custom-writing'}, async (_ctx, config) => {
    assert.equal(config.serverName, 'custom-writing')
    assert.equal(config.failOnStartupError, true)
    events.push('ready')
  })
  assert.deepEqual(events, ['ready', 'section'])
  assert.equal(sections[0].interpolate, false)
  assert.match(sections[0].text, /mcp__custom-writing__compile_generation_prompt/)
  assert.match(sections[0].text, /not code or ordinary answers/)
})

test('disabled generation guidance retains tools, failed startup contributes no section', async () => {
  let mounted = false
  await mountWritingPlugin({}, {generationGuidance: false}, async () => { mounted = true })
  assert.equal(mounted, true)
  let registered = false
  await assert.rejects(mountWritingPlugin({systemPrompt: {section: () => {registered = true}}}, {}, async () => {
    throw new Error('startup failed')
  }), /startup failed/)
  assert.equal(registered, false)
  assert.throws(() => resolveServerConfig({serverName: 'bad name'}), /serverName/)
  assert.throws(() => resolveServerConfig({toolCallTimeoutMs: -1}), /toolCallTimeoutMs/)
})

test('bundled Python server negotiates, compiles genres, verifies facts, and blocks escapes', {timeout: 20000}, async () => {
  const root = mkdtempSync(join(tmpdir(), 'human-writing-dsh-'))
  writeFileSync(join(root, 'humanwriting.py'), 'raise RuntimeError("workspace shadowed runtime")')
  writeFileSync(join(root, 'sources.md'), 'Observed test: the device lasted six hours.', 'utf8')
  assert.throws(() => resolveServerConfig({root: join(root, 'sources.md')}), /must be a directory/)
  const config = resolveServerConfig({root})
  const child = spawn(config.command, config.args, {cwd: config.cwd, stdio: ['pipe', 'pipe', 'pipe']})
  const responses = new Map()
  let stderr = ''
  child.stderr.on('data', data => {stderr += data})
  const lines = createInterface({input: child.stdout})
  lines.on('line', line => {
    const value = JSON.parse(line)
    const pending = responses.get(value.id)
    if (pending) {responses.delete(value.id); pending.resolve(value)}
  })
  child.on('error', error => { for (const pending of responses.values()) pending.reject(error) })
  child.on('exit', code => { for (const pending of responses.values()) pending.reject(new Error(`Server exited ${code}: ${stderr}`)) })
  let id = 0
  const request = (method, params = {}) => new Promise((resolve, reject) => {
    responses.set(++id, {resolve, reject})
    child.stdin.write(JSON.stringify({jsonrpc: '2.0', id, method, params}) + '\n')
  })
  const call = (name, args) => request('tools/call', {name, arguments: args})
  try {
    const initialized = await request('initialize', {protocolVersion: '2025-03-26', capabilities: {}, clientInfo: {name: 'dsh-test', version: '1'}})
    assert.equal(initialized.result.serverInfo.version, '0.16.1')
    const listed = await request('tools/list')
    assert.ok(listed.result.tools.some(tool => tool.name === 'compile_generation_prompt'))
    for (const style of ['fiction', 'academic-paper', 'formal-document']) {
      const compiled = await call('compile_generation_prompt', {style, task: 'Write the requested passage.'})
      assert.equal(compiled.result.isError, undefined)
      assert.match(compiled.result.content[0].text, /generation-quality/)
    }
    const report = await call('compile_generation_prompt', {style: 'self-media', task: 'Explain the test.', source_paths: ['sources.md']})
    assert.match(report.result.content[0].text, /device lasted six hours/)
    const escaped = await call('compile_generation_prompt', {style: 'self-media', task: 'Write.', source_paths: ['../outside.md']})
    assert.equal(escaped.result.isError, true)
    const fidelity = await call('verify_fidelity', {source_text: 'The effect may be 20%.', candidate_text: 'The effect is 20%.'})
    assert.equal(JSON.parse(fidelity.result.content[0].text).status, 'needs-review')
  } finally {
    const closed = once(child, 'close')
    child.stdin.end()
    child.kill()
    await closed
    lines.close()
    assert.equal(dirname(resolve(root)), resolve(tmpdir()))
    assert.ok(basename(root).startsWith('human-writing-dsh-'))
    rmSync(root, {recursive: true, force: true})
  }
})
