import { apply as applyMcpClient } from '@deepseek-ai/dsh-mcp-client'

export const name = 'advanced-human-writing'
export const inject = ['tools']

/**
 * DeepSeek Harness bundle adapter. The Python package owns audit planning and
 * state; this thin plugin only mounts it as a stable, namespaced MCP toolset.
 */
export async function apply(ctx, config = {}) {
  const root = config.root ?? process.cwd()
  const pythonCommand = config.pythonCommand ?? process.env.PYTHON ?? 'python'
  const serverName = config.serverName ?? 'human-writing'
  await applyMcpClient(ctx, {
    transport: 'stdio',
    serverName,
    command: pythonCommand,
    args: ['-m', 'humanwriting.mcp_server', '--root', root],
    env: config.env ?? {},
    cwd: root,
    toolCallTimeoutMs: config.toolCallTimeoutMs ?? 60000,
    failOnStartupError: true,
  })
}
