# Human Writing Skills

> 让 AI 写作代理读取可复用的 `SKILLS`，写出更自然、更连贯、更有文体意识的文字。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](pyproject.toml)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](pyproject.toml)

中文说明 | [English](README.md)

Human Writing Skills 是一个开源的 AI 写作技能包，也带有一个轻量级命令行工具。它把“写得自然一点”“不要有 AI 味”“长文不要忘设定”这些模糊要求，拆成 AI 能执行、能检查、能复用的 Markdown `SKILLS`。

它适合小说、网文、议论文、新闻报告、自媒体文章、科研论文等不同写作场景。项目重点不是伪装作者身份，而是提升 AI 辅助写作的质量：减少模板腔，增强上下文衔接，让文本更像经过人类编辑认真处理过。

## 这个项目解决什么

| 常见问题 | 项目提供的办法 |
| --- | --- |
| 文字空泛、对称、像模板 | 用具体的修订检查项压掉套话和泛泛表达 |
| 不同文体都写成一种味道 | 为不同文体提供独立 `SKILLS` |
| 长文本容易忘记剧情和设定 | 使用轻量级 ledger 记录人物、规则、伏笔和状态 |
| 提示词越写越乱 | 用 CLI 把文体、上下文、任务编译成清晰指令包 |
| “像人写的”太抽象 | 把自然感拆成节奏、细节、转场、视角、证据等可执行规则 |

## 已内置的基础文体 SKILLS

| Skill | 适合场景 | 重点 |
| --- | --- | --- |
| `fiction` | 小说/故事 | 视角、人物行为、场景压力 |
| `argumentative` | 议论文/观点文 | 论点、证据、反驳、逻辑推进 |
| `news-report` | 新闻报告 | 事实顺序、消息来源、克制表达 |
| `self-media` | 自媒体文章 | 有用、直接、有个人判断，但不空喊口号 |
| `academic-paper` | 科研论文 | 谨慎表述、结构、术语一致性 |
| `webnovel` | 网络小说/连载文 | 爽点、钩子、伏笔回收、战力和设定连续性 |

## 深层“人类痕迹”模块

这些模块不是做表面替换，而是处理更深的 AI 写作痕迹。

| Module | 修复什么 |
| --- | --- |
| `controlled-drift` | 逻辑过度顺滑、缺少联想跳跃、没有未完成思考 |
| `narrative-bridges` | 场景转折弱、万能转场多、段落之间没有因果和压力传递 |
| `imperfect-prose` | 文字太干净、太对称、太像统一润色 |
| `vocal-rhythm` | 朗读时节奏单调、缺少呼吸点 |
| `embodied-emotion` | 只有情绪标签，没有身体、动作、矛盾和感知 |
| `cultural-anchors` | 文本像发生在真空里，没有时代、地域、社群和物质细节 |
| `style-matrix` | 避免把一种“人类口吻”套到所有文体上 |
| `editor-loop` | 建立挑剔编辑式的审查与局部重写流程 |
| `ai-trace-rubric` | 把“还像 AI”拆成可诊断、可修复的维度 |

## 快速开始

```powershell
git clone https://github.com/whh110112/human-writing-skills.git
cd human-writing-skills

python -m humanwriting.cli list --kind style
python -m humanwriting.cli list --kind module
python -m humanwriting.cli build --style webnovel --context examples/story-ledger.md --task "续写第三章，保留冲突但揭示一个新线索。"
```

`build` 命令会输出一份可以直接复制给 Codex、ChatGPT、Claude、本地大模型或其他写作代理的指令包。

## 指令包长什么样

```text
# Core Directive
# Continuity Protocol
# Selected Skill: webnovel
# Project Context
# Task
# Output Contract
```

它会把通用写作原则、长上下文协议、选中的文体技能、项目设定和本次任务放在一起，让 AI 不只是“知道主题”，还知道前文承诺了什么、哪些设定不能改、下一段必须从哪里接上。

## 长文本连续性方案

长篇小说、网文、系列文章最容易出问题的地方，不是单句写不好，而是写着写着忘了：

- 人物关系变过没有
- 伤势、代价、能力限制还在不在
- 某个伏笔是否已经揭示
- 论证前后有没有自相矛盾
- 上一段结束时人物到底在哪里

因此项目使用轻量级 ledger 记录：

- 固定事实：人物、时间线、地点、关系、规则
- 活跃线索：未解决冲突、悬念、伏笔、论点
- 声音锚点：叙述视角、语气、节奏、禁用表达
- 当前状态：上一段结束在哪里，下一段必须如何衔接
- 节拍桥：上一拍留下什么、下一拍为什么开始、中间发生什么微转折、结尾留下什么压力
- 新增事实：本次输出后哪些事情变成了真

示例见：[examples/story-ledger.md](examples/story-ledger.md)

## Chatbox 使用

可以在 Chatbox 里用。这个项目生成的是纯文本指令包，不需要插件。长篇写作时，把 continuity ledger 当成上下文来源，并把编译后的指令包粘贴到 Chatbox 的 system prompt 或新会话第一条消息。

- 中文指南：[docs/chatbox.zh-CN.md](docs/chatbox.zh-CN.md)
- 英文指南：[docs/chatbox.md](docs/chatbox.md)
- 账本模板：[examples/chatbox-ledger-template.md](examples/chatbox-ledger-template.md)

## 项目结构

```text
humanwriting/        Python 包和 CLI
skills/              可复用 Markdown 写作 SKILLS
examples/            剧情账本、文章 brief 示例
tests/               标准库单元测试
```

## 常用命令

列出所有文体：

```powershell
python -m humanwriting.cli list
```

生成指令包：

```powershell
python -m humanwriting.cli build `
  --style fiction `
  --module controlled-drift `
  --module narrative-bridges `
  --module embodied-emotion `
  --module vocal-rhythm `
  --review `
  --context examples/story-ledger.md `
  --task "写下一场戏，保持林乔的听觉代价设定，不要提前解决冲突。"
```

`--review` 会自动加入两个模块：

- `editor-loop`：先生成，再以挑剔编辑视角诊断，局部重写，最后定稿
- `ai-trace-rubric`：从认知平滑、表达泛化、情感平面、节奏单调、上下文漂移、文化真空、过度干净、结论成瘾等维度评分

运行测试：

```powershell
python -m unittest discover -s tests -v
```

## 写作理念

这个项目认为，“去 AI 味”不能只靠一句提示词。更可靠的做法是让模型持续遵守几类具体约束：

- 有现场：知道谁在说话、发生了什么变化、这一段为什么存在
- 有细节：用属于当前题材的具体材料，而不是万能句子
- 有连续性：尊重前文事实、伤势、代价、伏笔、论点和情绪变化
- 有文体：先理解小说、新闻、论文、自媒体的不同读者期待
- 有修订：删除空话、套话、万能转场和不必要的拔高

## 编辑边界

这个项目不承诺“完美隐藏作者身份”或“绕过检测器”。它关注的是写作工艺：声音、上下文、文体、修订和连续性。

如果要从出版物中提炼技法，请使用简短分析、公版文本、授权材料或自写示例。不要把受版权保护的大段原文复制进 skill。

## 贡献方向

欢迎贡献更多中文和英文写作技能，例如：

- 商业报告
- 法律文书
- 演讲稿
- 短视频脚本
- 产品文案
- 人物传记
- 悬疑、科幻、都市、玄幻等细分网文技能
- 不同模型的适配器和示例

请尽量写具体规则，不要只写“自然一点”“像人一点”。好的 `SKILL` 应该告诉模型：做什么、避开什么、如何衔接、怎样检查。

## 开源协议

MIT. 见 [LICENSE](LICENSE)。
