import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')

export function resolveServerConfig(config = {}) {
  const root = resolve(config.root ?? process.cwd())
  if (!existsSync(resolve(packageRoot, 'humanwriting/mcp_server.py'))) {
    throw new Error('Writing runtime is missing. Install the repository-root bundle or the published release tarball.')
  }
  const command = config.pythonCommand ?? process.env.PYTHON ?? 'python'
  if (typeof command !== 'string' || !command.trim()) throw new Error('pythonCommand must be an executable path.')
  const serverName = config.serverName ?? 'human-writing'
  if (!/^[A-Za-z0-9_-]{1,32}$/.test(serverName)) throw new Error('serverName must contain 1–32 letters, numbers, underscores, or hyphens.')
  const timeout = config.toolCallTimeoutMs ?? 60000
  if (!Number.isSafeInteger(timeout) || timeout < 1000) throw new Error('toolCallTimeoutMs must be an integer of at least 1000.')
  if (!existsSync(root)) throw new Error('Writing workspace does not exist.')
  return {
    transport: 'stdio', serverName, command,
    // -I ignores user-site and PYTHONPATH. Import only the bundled runtime before
    // considering the writing workspace, which may itself contain Python files.
    args: ['-I', '-X', 'utf8', '-c',
      'import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); runpy.run_module("humanwriting.mcp_server",run_name="__main__")',
      packageRoot, '--root', root],
    env: {}, cwd: root, toolCallTimeoutMs: timeout, failOnStartupError: true,
  }
}

export function writingGuidance(serverName = 'human-writing') {
  const tool = name => `mcp__${serverName}__${name}`
  return `# Human Writing for DSH\n\nApply only to requested authored prose, rewriting, or editorial review, not code or ordinary answers.
For novels use fiction/webnovel; for papers academic-paper; for reports formal-document;
for news news-report; for essays argumentative; for posts self-media. Respect the user's language.
Before substantive writing, call ${tool('compile_generation_prompt')} with the task, style,
supplied context, and source_paths/reference_paths when available. Apply its instructions
while composing. For supplied-draft cleanup use ${tool('compile_humanize_prompt')}.
Use ${tool('compile_critique_prompt')} when the user wants advice rather than replacement text.
Keep factual evidence separate from voice references; never invent a citation, result,
personal experience, or source-backed detail. When necessary evidence is missing, narrow
the claim or identify missing input. Maintain fiction ledgers across chapters.
Before delivering substantial prose, use ${tool('lint_text')} as an editorial lead, not a
mandatory rewrite gate. Repair only evidenced defects. For rewrites check ${tool('verify_fidelity')}
and ${tool('verify_protected_content')}; unchanged numbers do not establish unchanged meaning.
Use focused audits when needed, not every audit on every paragraph. Long-form reviews
use the plan/claim/receipt/coverage tools. Do not claim naturalness or publish externally
solely because a lint score improved. Write or save content through DSH's normal output
tools when requested; publishing to an external destination needs that user's instruction.
\n${readFileSync(resolve(packageRoot, 'skills/generation-quality.md'), 'utf8')}`
}

export async function mountWritingPlugin(ctx, config, mountMcp) {
  const serverConfig = resolveServerConfig(config)
  await mountMcp(ctx, serverConfig)
  if (config.generationGuidance !== false) {
    ctx.systemPrompt.section({
      name: `human-writing:${serverConfig.serverName}`, order: 7500,
      interpolate: false, text: writingGuidance(serverConfig.serverName),
    })
  }
}
