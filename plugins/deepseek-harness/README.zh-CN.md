# Advanced Human Writing 的 DeepSeek Harness 插件

此 Bundle 把主项目的 `human-writing-mcp` 工具挂载到 DeepSeek Harness。它在
本地协调长篇审查：生成分块计划、让独立 Agent 领取任务、要求提交完整覆盖回执，并且只在
验证通过后开放最终统稿。

## 前置条件

先在 `PYTHON` 或 `python` 对应的环境安装主项目：

```powershell
pip install human-writing-skills
```

从本仓库开发时：

```powershell
pip install -e .
```

## 安装

本目录发布到 npm 后，执行：

```powershell
dsh plugin --profile web add dsh-advanced-human-writing
```

重启相应 DSH profile。插件默认以当前工作区为可访问根目录；若 Python 解释器名称不是
`python`，请在启动 DSH 前设置 `PYTHON`。

插件提供计划、领取、提交、覆盖验证、统稿领取与账本读取工具。它不自行调用模型，也不会把
草稿发送到第三方；每名 Agent 只审查自己的任务并提交报告。
