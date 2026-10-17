# DSH 人类写作与去 AI 味插件

用于在 DeepSeek Harness 中生成小说、论文、报告、议论文和自媒体内容，并润色已有草稿。
插件在生成前提供精简写作协议，挂载文体提示编译、套话扫描、原意保真、声音保留和
长文分块审查工具。文字由当前 DSH 代理完成，插件不会额外调用模型。

## 安装

需要 Python 3.9+，以及有 tools / systemPrompt 服务的 DSH profile。
已用官方 0.2.1-alpha.2 包完成集成测试；声明的兼容范围还包括 0.2.0-rc.2 和
0.2.1 alpha 系列，其他版本尚未实测。Node 要求 ^22.19.0 或 >=24.0.0。
安装包自带本项目 Python 核心和写作模块，不需要额外 pip 安装 human-writing-skills。

```powershell
dsh plugin --profile web add https://github.com/whh110112/human-writing-skills/releases/download/dsh-v0.2.1/dsh-advanced-human-writing.tgz
```

桌面版把 `web` 换成 `desktop`，安装后重启对应 profile。如果解释器不叫 `python`，
在启动 DSH 前把 `PYTHON` 设置为 Python 可执行文件路径。
也可安装仓库根目录的固定标签：

```powershell
dsh plugin --profile web add github:whh110112/human-writing-skills#dsh-v0.2.1
```

真正可分发的 package.json 在仓库根目录；本适配子目录为 private，不单独发布。
当前分发渠道为 GitHub Release，不声称已经发布 npm 包。

## 在 DSH 中使用

- 小说：“使用 Human Writing 续写这个重逢场景，保留人物设定，让对白有回应，不要追加感悟式结尾。”
- 论文：“根据这些观察写结果段落，保留不确定性，不编造引文、数据或显著性检验。”
- 报告：“写本周进度报告，交代现状、阻碍、责任人与下一步，区分计划和已完成事项。”
- 润色：“保留我的原意和口吻，修改套话与重复结构，不添加不存在的经历。”
- 诊断：“只指出这篇文章的问题，不代写。”

插件向模型说明：仅在用户请求写作、改写或审稿时应用规则，实质写作前先调用
`mcp__human-writing__compile_generation_prompt`，根据返回的文体协议生产文字；
需要时调用 lint 和保真工具再交付。生成前约束空泛开头、机械对比、冗余解释、
装饰性细节、翻译腔和无意义升华。允许正式文风、直接情绪表达和必要重复。
规则依赖模型遵循，不能保证所有模型每次都执行，也不保证检测器分数。

事实材料用工作区相对路径 `source_paths`，文风样本用 `reference_paths`，两者不能混用。
工具拒绝越出工作区的路径；小说不会自动开启事实文档来源审查。
输入示例见 [examples](examples)，无 API 密钥的真实集成过程见 [DEMO.md](DEMO.md)。

## 配置与权限

`root` 默认 DSH 启动工作目录，建议设置为写作项目目录；`pythonCommand` 默认
PYTHON 或 python；`serverName` 默认 human-writing；`generationGuidance: false`
可关闭系统提示，只保留工具；`toolCallTimeoutMs` 默认 60000。

启动本地 Python stdio 进程，隔离模式优先加载包内核心，避免项目文件冒充核心。
工具按调用读取文字和工作区资料，长文工具按调用写入审查包，不自动上传稿件、
不开放网络端口、不自动安装 Python 依赖，也不自动发布生成文章。
文本进入当前 DSH 模型上下文时，仍遵循用户现有模型供应商的隐私设置。

分类：Skills / Tools & Capabilities。许可证：MIT。社区插件，非 DeepSeek 官方产品。
可安装版本发布与市场审核收录是两个独立步骤。
