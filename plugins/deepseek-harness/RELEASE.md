DSH Writing Plugin 0.3.0 bundles Human Writing core 0.17.0 and all writing modules.

## 多 Agent 长篇写作

- 从大纲开始，依次完成大纲检查、分块规划、逐块写作、逐块独立审稿和全局衔接审核。
- 六万字符、每块五千字符规划为十二个写作任务及对应审稿任务；默认按依赖执行，显式独立契约允许受限并行。
- 交接累计事实状态和待承接事项，检查过渡证据、段落覆盖和相邻块；返修使受影响的后续结果失效。
- 详细编排协议按需加载，宿主缺少原生子代理执行器时明确说明角色轮次降级。

## Multi-Agent Long-Form Writing

The plugin adds outline checking, block planning, writers, independent per-block
editors, and final continuity review. Explicit state contracts govern parallel
blocks; sequential dependencies remain the default. Claims and versioned results
prevent stale workers or outdated approvals from entering final assembly.

Install:

```sh
dsh plugin --profile web add https://github.com/whh110112/human-writing-skills/releases/download/dsh-v0.3.0/dsh-advanced-human-writing.tgz
```

Use `desktop` for a desktop profile. Requires Python 3.9+ on PATH (or an explicit
pythonCommand) and Node ^22.19.0 or >=24. Tested with official DSH 0.2.1-alpha.2
Cordis/MCP packages. Actual native delegation requires the host's subagent service,
provider, tool and model driver. Live-model child execution has not been exercised.

Validation: 230 Python tests completed successfully with one environment-dependent
skip locally; seven DSH integration tests and isolated tarball verification passed.
