import assert from 'node:assert/strict'
import { test } from 'node:test'
import { Context } from '@deepseek-ai/cordis'
import SystemPrompt, { renderPrompt } from '@deepseek-ai/dsh-system-prompt'
import ToolRuntime from '@deepseek-ai/dsh-tools'
import * as WritingPlugin from '../index.js'

test('official Cordis + MCP mounts, assembles writing guidance, calls tools, and unloads', {timeout: 20000}, async () => {
  const ctx = new Context()
  try {
    await ctx.plugin(SystemPrompt)
    await ctx.plugin(ToolRuntime)
    const plugin = ctx.plugin(WritingPlugin, {serverName: 'writing-integration'})
    await plugin
    const name = 'mcp__writing-integration__compile_generation_prompt'
    assert.ok(ctx.tools.get(name), 'MCP tool is discovered through the official client')
    const prompt = renderPrompt(await ctx.systemPrompt.assemble({}))
    assert.match(prompt, /Human Writing for DSH/)
    const result = await ctx.tools.execute({
      signal: new AbortController().signal, callId: 'writing-test-1', name,
      arguments: {style: 'academic-paper', task: 'Describe the supplied results without inventing citations.'},
    })
    assert.equal(result.isError, false)
    assert.match(result.content[0].text, /generation-quality/)
    await plugin.dispose()
    assert.equal(ctx.tools.get(name), undefined)
    assert.doesNotMatch(renderPrompt(await ctx.systemPrompt.assemble({})), /Human Writing for DSH/)
  } finally {
    await ctx.fiber.dispose()
  }
})
