# Advanced Human Writing Skills

> 让 AI 写作代理读取可复用的 `SKILLS`，写出更自然、更连贯、更有文体意识的文字。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](pyproject.toml)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](pyproject.toml)

中文说明 | [English](README.md)

Advanced Human Writing Skills 是一个开源、模块化的中英文 AI 写作技能包，也带有一个轻量级命令行工具。它把“写得自然一点”“不要有 AI 味”“长文不要忘设定”这些模糊要求，拆成 AI 能执行、能检查、能复用的 Markdown `SKILLS`。为兼容已有安装和链接，Python 包名、GitHub 仓库名与 ClawHub slug 继续使用 `human-writing-skills`。

它适合小说、网文、议论文、新闻报告、自媒体文章、科研论文等不同写作场景。项目重点不是伪装作者身份，而是提升 AI 辅助写作的质量：减少模板腔，增强上下文衔接，让文本更像经过人类编辑认真处理过。

## 这个项目解决什么

| 常见问题 | 项目提供的办法 |
| --- | --- |
| 文字空泛、对称、像模板 | 用具体的修订检查项压掉套话和泛泛表达 |
| 反复“不是……是……”“是……不是……”或“比……比……” | 检查句式家族与复现密度，保留必要纠错和真实比较，重写装饰性框架 |
| 改写时悄悄改变事实、语气强度、不确定性或因果 | 仅在提供原文时启用语义保真账本与新增细节检查 |
| 句子表面流畅却漏字、漏宾语或连接成分 | 用句法槽位、并列对称和指代回查做独立终校 |
| 模糊归因、意义拔高、假范围、同义词轮换和排版套路反复出现 | 按文体和密度审查表层模式，不搞全局禁词 |
| 不同文体都写成一种味道 | 为不同文体提供独立 `SKILLS` |
| 长文本容易忘记剧情和设定 | 使用轻量级 ledger 记录人物、规则、伏笔和状态 |
| 人物对白像同一个人或不合当下身份 | 按人物基线、谈话目的、知识边界、听众和压力生成并审核 |
| 关键台词或动作后无人承接，剧情生硬切走 | 检查回应义务，并把延迟回应记录为互动欠账 |
| 时代、技术、制度或世界规则互相冲突 | 抽取世界契约，再检查物件、行动和例外是否兼容 |
| 调查、谈判、研发等过程被跳过，结果凭空成功 | 检查承诺、尝试、阻力、判断、代价和结果的赚取链 |
| 扩写只增加环境、心理和同义复述 | 比较场景承诺与注意力分配，把篇幅还给关键过程和后果 |
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
| `relationship-state` | 人物关系重置、对白没有主动权变化、秘密和边界被遗忘 |
| `relationship-stance-audit` | 检查“谁在谁面前提谁”：敌对、多角、阵营、上下级、掌门/家族等关系立场错误 |
| `logic-causality-audit` | 检查因果、时间线、知识来源、动机、规则、资源和后果断裂 |
| `character-consistency-audit` | 检查人物目标、声音、能力、边界、知识和转变是否有过渡 |
| `dialogue-voice-audit` | 按人物基线与情境生成并审核对白，检查关键回合是否得到语言、动作、沉默或延迟回应 |
| `serial-reentry` | 有前章或账本时，检查前情倾倒、遗漏承接和章节状态重置 |
| `chapter-momentum-audit` | 检查只铺气氛不推进、承诺未兑现、章间残留丢失和无依据钩子 |
| `world-ontology-audit` | 检查时代、技术、制度、社会习惯和架空规则是否兼容 |
| `process-earnedness-audit` | 检查关键结果是否由选择、阻力、证据和代价赚到 |
| `attention-budget-audit` | 检查低价值描写、语义回声和无状态变化扩写是否挤占核心内容 |
| `chapter-pattern-audit` | 对三章以上提取结构指纹，识别重复开场、转折、情绪峰值和钩子模板 |
| `narrative-distance-control` | 检查无动机拉近镜头、缺少场景定位和叙事距离漂移 |
| `imagery-load-audit` | 检查比喻堆叠、感官争抢和展示动作后重复解释情绪 |
| `paragraph-rhythm-audit` | 检查机械单行段落连发和塞入过多转折的长段 |
| `detail-disclosure-audit` | 检查人物履历、身材和外貌在剧情使用前集中倾倒 |
| `scene-entry-audit` | 检查精确时间、地点、光线天气、全套穿着和概括情绪同时挤在开场 |
| `natural-measurement` | 虚假精确：小说里不合语境的微小精确量化和机械计数 |
| `cliche-phrase-audit` | 论坛常吐槽的塑料套话、万能身体动作、空洞情绪标签和死转场 |
| `formulaic-structure-audit` | 过于整齐的三连式、双向“不是/是”对举、连续“比”比较和每段干净收束 |
| `prose-progress-audit` | 段落没有新增状态，或关键台词/动作尚未被接收就切换话题与场景 |
| `imperfect-prose` | 文字太干净、太对称、太像统一润色 |
| `vocal-rhythm` | 朗读时节奏单调、缺少呼吸点 |
| `embodied-emotion` | 只有情绪标签，没有身体、动作、矛盾和感知 |
| `cultural-anchors` | 文本像发生在真空里，没有时代、地域、社群和物质细节 |
| `spatial-blocking` | 防止车内、房间、电梯等狭小空间里人物瞬移 |
| `occupancy-capacity` | 检查座位、长椅、床、板凳、过道等物理资源是否超容量或形态不明 |
| `appearance-prop-continuity` | 防止服装、鞋子、道具、伤口等日常细节漂移 |
| `physical-continuity-audit` | 输出前检查座位、站位、移动过渡、服装道具一致性 |
| `proofreading-audit` | 最后检查错漏字、谓词必需成分、悬空连接词、指代、标点、称谓和排版 |
| `style-matrix` | 避免把一种“人类口吻”套到所有文体上 |
| `editor-loop` | 建立挑剔编辑式的审查与局部重写流程 |
| `ai-trace-rubric` | 把“还像 AI”拆成可诊断、可修复的维度 |
| `reference-style-alignment` | 只在明确提供参考资料或文风要求时，提炼可迁移的声音与写法，不复制内容 |
| `rewrite-fidelity` | 提供原文时检查意义漂移、凭空具体化、正反颠倒和不确定性变化 |
| `surface-pattern-audit` | 按文体审查表层模式家族，包括装饰性连续比较，但不全局封禁句式 |
| `protected-content` | 防止润色时误改数字、引文、公式、链接、代码、原话和指定术语 |
| `source-grounding` | 严肃文本有明确来源时，核对主张、出处、适用范围和不确定性 |

## 快速开始

```powershell
git clone https://github.com/whh110112/human-writing-skills.git
cd human-writing-skills
python -m pip install .

human-writing-skills list --kind style
human-writing-skills list --kind module
human-writing-skills build --style webnovel --context examples/story-ledger.md --task "续写第三章，保留冲突但揭示一个新线索。"
```

也可以不安装，继续使用 `python -m humanwriting.cli ...`。`build` 命令会输出一份可以直接复制给 Codex、ChatGPT、Claude、本地大模型或其他写作代理的指令包。

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

## 明确触发的参考文风

参考文风模块默认关闭。只有传入 `--reference`、传入 `--reference-style`，或任务
中明确出现“参考/贴近/沿用某种文风”等要求时才激活。单独传入剧情账本或前文
章节作为 `--context` 不会误触发。

```powershell
human-writing-skills build `
  --style fiction `
  --context examples/story-ledger.md `
  --reference examples/reference-style-source.zh-CN.md `
  --task "续写下一场，贴近参考材料的克制节奏。"

human-writing-skills audit `
  --draft my-chapter.md `
  --reference examples/reference-style-source.zh-CN.md `
  --profile style-match
```

模块会提炼视角、句长节奏、词汇层级、意象密度、场景和人物描写方法、对白
节拍、情绪表达和转场方式。剧情事实仍以 `--context` 为准，不得复制参考资料的
人名、事件或标志性句子。详见 [docs/reference-style.zh-CN.md](docs/reference-style.zh-CN.md)。

## 原文改写保真

只有改写现有文字并且必须保持原意时才传入 `--original`。它会为生成或审稿单独
加载语义保真模块；普通创作不会承担这部分 Token。

```powershell
human-writing-skills build `
  --style self-media `
  --original original.md `
  --task "在不增加事实、不强化结论的前提下改得更清楚。"

human-writing-skills audit `
  --draft revised.md `
  --original original.md `
  --profile fidelity
```

`--original` 是改写语义依据，`--reference` 只提供文风依据，`--source` 只为严肃
文本提供事实证据。三种材料隔离加载，避免范文改写事实，也避免原文被误当成模仿
目标。详见 [docs/editing-tools.zh-CN.md](docs/editing-tools.zh-CN.md)。

## 严肃文本来源依据

`--source` 与 `--reference` 完全分离。它只在论文、新闻、法律或技术文本中
激活 `source-grounding`，建立“主张 -> 来源位置 -> 支持范围 -> 结论”的证据表。
小说、网文、自媒体和普通问答不会自动加载。

```powershell
human-writing-skills audit `
  --draft paper.md `
  --document-type academic-paper `
  --source study-a.md `
  --source study-b.md `
  --profile sources
```

来源核验会区分“文献存在”和“文献支持当前结论”。没有外部数据库访问时，只会
把 DOI、标准、判例或元数据标为待核验，不会猜测真实性。

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
- 关系状态：谁知道、想要、隐瞒、亏欠、拒绝了什么，谁握有主动权
- 关系立场：公开/私下态度、当前听众、谁能在谁面前提谁、禁泄秘密和例外动机
- 声音锚点：叙述视角、用词、直接程度、披露习惯、知识边界、听众变化和禁用表达
- 对话契约：谁对谁说、为何现在说、想让对方做什么、不能透露什么、这轮要改变什么
- 互动欠账：哪句关键台词或动作仍待回应、拒绝、打断、后果或延迟回收
- 当前状态：上一段结束在哪里，下一段必须如何衔接
- 节拍桥：上一拍留下什么、下一拍为什么开始、中间发生什么微转折、结尾留下什么压力
- 新增事实：本次输出后哪些事情变成了真

示例见：[examples/story-ledger.md](examples/story-ledger.md)

## Chatbox 使用

可以在 Chatbox 里用。这个项目生成的是纯文本指令包，不需要插件。长篇写作时，把 continuity ledger 当成上下文来源，并把编译后的指令包粘贴到 Chatbox 的 system prompt 或新会话第一条消息。

- 中文指南：[docs/chatbox.zh-CN.md](docs/chatbox.zh-CN.md)
- 英文指南：[docs/chatbox.md](docs/chatbox.md)
- 账本模板：[examples/chatbox-ledger-template.md](examples/chatbox-ledger-template.md)

## 物理连续性

如果写车内、房间、电梯、餐桌、病房等空间关系很重要的场景，使用 `--strict-continuity`。它会自动加入容量、空间调度、服装道具等生成约束；成稿法医式物理审查由 `audit --profile physical` 负责。

```powershell
python -m humanwriting.cli build `
  --style fiction `
  --strict-continuity `
  --review `
  --context examples/vehicle-scene-ledger.md `
  --task "续写车内争执。任何座位变化都必须写出动作过渡，保持服装和道具状态一致。"
```

- 说明：[docs/physical-continuity.zh-CN.md](docs/physical-continuity.zh-CN.md)
- 车辆场景账本：[examples/vehicle-scene-ledger.md](examples/vehicle-scene-ledger.md)
- 容量账本模板：[examples/capacity-ledger-template.md](examples/capacity-ledger-template.md)
- 容量冲突示例：[examples/capacity-conflict-draft.zh-CN.md](examples/capacity-conflict-draft.zh-CN.md)
- 成稿审查示例：[examples/problem-car-scene-draft.zh-CN.md](examples/problem-car-scene-draft.zh-CN.md)

## 关系立场连续性

如果对话涉及敌对关系、多角关系、门派/家族/公司阵营、上下级或秘密关系，使用 `--deep-review` 或显式加入 `relationship-stance-audit`。它会把每句对话抽成“说话人 -> 听话人/在场观众 -> 被提及第三方”，检查是否存在无动机的夸敌人、骂盟友、泄露隐藏关系、称谓错位或信息权限错误。

- 说明：[docs/relationship-stance-continuity.zh-CN.md](docs/relationship-stance-continuity.zh-CN.md)
- 关系账本模板：[examples/relationship-stance-ledger.zh-CN.md](examples/relationship-stance-ledger.zh-CN.md)

## 人物与情境对白

`dialogue-voice-audit` 把对白拆成三层：人物长期语言基线、当前场景对基线的
调制，以及每句话试图完成的行动。职业、阶层、地域和性格标签只能提供知识、
利益、责任与语域变化线索，不能直接替代人物性格。生成时明确要求言语中心场景
即可按需激活；已有稿件使用独立 `voice` 审稿：

```powershell
human-writing-skills audit `
  --draft my-dialogue-scene.md `
  --context my-novel-ledger.md `
  --profile voice
```

审核会区分“设定冲突”和“有动机的反差”，并检查谈话目的、知识边界、现实约束、
上一句回应、听众与权力关系。关键台词或动作不要求机械地回一句话，但在转场前
必须有语言、动作、可读的沉默、明确打断或延迟回应；否则会标记为互动回合悬空。

如果已经有一段文本需要审稿，使用 `audit`：

```powershell
python -m humanwriting.cli audit `
  --draft examples/problem-car-scene-draft.zh-CN.md `
  --context examples/vehicle-scene-ledger.md
```

## 项目结构

```text
humanwriting/        Python 包和 CLI
skills/              可复用 Markdown 写作 SKILLS
examples/            剧情账本、文章 brief 示例
tests/               标准库单元测试
```

## 常用命令

### 按需叙事模块

新增能力采用渐进加载。生成任务只有明确要求对话、谈判、会谈、审问、争论等
言语中心场景时，才自动加入 `dialogue-voice-audit`；普通叙述和严肃文体不会误触发。
审稿中的 `voice`、`serial`、`world`、`process`、`momentum`、`salience`、
`recurrence`、`texture`、`sources` 仍不塞入宽覆盖的 `full`：

```powershell
human-writing-skills build --style fiction --task "写一场两位角色各有所求的谈判。"
human-writing-skills build --style webnovel --context ledger.md --module serial-reentry --task "续写第18章。"
human-writing-skills audit --draft chapters.md --profile momentum
human-writing-skills audit --draft chapter.md --profile texture
human-writing-skills audit --draft chapter.md --profile process
human-writing-skills audit --draft chapters.md --profile recurrence
```

`dialogue-voice-audit` 不按职业套口吻，而是检查稳定语言基线、现实利益、知识边界、
当场目标、回应关系和有动机的变调；`serial-reentry` 只有提供前章或账本
时才可使用；`momentum` 只审多章稿件的入场压力、变化、回报和章尾承接；`texture`
负责电影式开场堆料、叙事距离、比喻与感官负载、单行段落成串、动作后重复解释
情绪以及人物资料倾倒。`world` 只在明确世界坐标出现时检查兼容性；`process`
检查关键结果是否由过程赚到；`salience` 只对长稿检查注意力预算；`recurrence`
至少需要三章；`sources` 需要严肃文体和明确来源文件。

生成时，`world`、`process` 和 `attention-budget-audit` 也只会分别在任务出现明确
世界设定、关键过程、扩写/长稿/灌水审查信号时加入，不随普通 `--deep-review` 加载。

### 审稿 Profile

`audit` 可以只加载当前需要的审查规则，避免无关模块干扰结果：

| Profile | 用途 |
| --- | --- |
| `full` | 宽覆盖默认审稿；高成本与强条件 Profile 保持独立 |
| `logic` | 因果、时间线、知识、动机、规则、资源与后果 |
| `character` | 人物目标、声音、能力、边界和变化桥梁 |
| `voice` | 人物基线、谈话目的、知识/角色约束、听众语域、变调依据和回应义务 |
| `serial` | 前情倾倒、遗漏承接和章节重置；必须提供 `--context` |
| `momentum` | 多章稿件的入场压力、不可逆变化、承诺回报、残留和章尾压力 |
| `world` | 时代、技术、制度、社会习惯和世界规则兼容性 |
| `process` | 承诺、尝试、阻力、判断、代价、证据与结果的赚取链 |
| `salience` | 长稿注意力分配、低价值扩写和跨段语义回声 |
| `recurrence` | 三章以上的章节结构指纹和模板复读 |
| `texture` | 叙事距离、场景入场负载、意象、段落节拍和资料投放 |
| `physical` | 座位、空间、容量、触达、服装、道具和伤势 |
| `relationship` | 关系立场、当前听众、信息权限、称谓和秘密泄露 |
| `ai-trace` | 套话、公式结构、段落无推进和其他 AI 痕迹 |
| `numbers` | 动作与情绪中的假精确数字 |
| `proofread` | 错漏字、句法槽位、悬空连接词、指代、标点、称谓和排版 |
| `fidelity` | 原意、实体、正反、不确定性、时间顺序、归因和新增细节；必须提供 `--original` |
| `style-match` | 对照明确输入的参考资料检查文风漂移；没有参考信号时不可使用 |
| `sources` | 对照明确来源核验严肃文本主张；需要 `--source` 和严肃文体 |

Profile 可以重复组合，例如 `--profile relationship --profile ai-trace`。

普通生成只加载一句轻量句法完整性检查。完整的漏字、缺宾语、悬空连接词和指代审查仅在
`proofread` 或流水线校对阶段加载，避免长期占用生成 Token。

### 多阶段流水线

需要高精度审稿时，不必让一个模型一次检查所有问题。`pipeline` 会为同一稿件生成多份职责独立的提示词：

```powershell
human-writing-skills pipeline `
  --draft my-chapter.md `
  --context my-novel-ledger.md `
  --auto `
  --output-dir chapter-audit
```

每个阶段应放到新的模型会话或独立 API 请求运行。自动模式会保留逻辑、AI 痕迹和校对，再按人物、关系、空间、精确数字、持续对白、世界坐标、关键过程、稿件长度和多章结构追加专项阶段。`serial` 需要账本；`fidelity` 需要原文；`salience` 只处理至少 4000 字符且段落充分的长叙事；`recurrence` 至少需要三章；`sources` 只有来源文件与严肃文体同时成立才加载。只有需要统计诊断时再加 `--with-stats`。清单会说明每项选择和跳过原因。

- 详细说明：[docs/audit-pipeline.zh-CN.md](docs/audit-pipeline.zh-CN.md)

### 确定性保护工具

`lint` 会给出规则编号、行列和原文证据；`stats` 提供可选的分布统计；`fix`
只预览保守的机械修复；`verify` 会比较改写前后受保护的数字、引文、公式、链接、
代码和术语。分数与统计只是透明的编辑启发式，不是 AI 作者身份鉴定。

内容保护只对论文、新闻以及具有充分证据的法律/技术文档自动加载。小说、网文、
普通问答、搞怪文本和自媒体默认不加载；需要例外时使用 `--protect-content` 或
`--protect-term` 明确开启。

```powershell
human-writing-skills lint --draft my-chapter.md --style fiction
human-writing-skills stats --draft my-chapter.md --style fiction
human-writing-skills fix --draft my-chapter.md --preview
human-writing-skills verify --source original.md --candidate revised.md --protect-term "星港计划"
```

- 痕迹扫描：[docs/pattern-linter.zh-CN.md](docs/pattern-linter.zh-CN.md)
- 改写保真、统计和保守修复：[docs/editing-tools.zh-CN.md](docs/editing-tools.zh-CN.md)
- 内容保护：[docs/protected-content.zh-CN.md](docs/protected-content.zh-CN.md)

### 数字必要性审查

用于处理“人物动作和情绪里不自然的 1 厘米、3 厘米、7 秒”等假精确感，同时保留建筑高度、伤口鉴定、工程参数、新闻事实等必要数字。

```powershell
python -m humanwriting.cli audit `
  --draft examples/false-precision-draft.zh-CN.md `
  --profile numbers
```

- 说明：[docs/number-sense.zh-CN.md](docs/number-sense.zh-CN.md)
- 示例：[examples/false-precision-draft.zh-CN.md](examples/false-precision-draft.zh-CN.md)

### 常见写作问题审查

本项目把长文本中反复出现的问题整理成可执行审查项：套话、塑料感、三连式结构、过度顺滑、段落无推进、空情绪、万能转场、文化真空和长文漂移。

- 规则映射：[docs/forum-complaint-research.zh-CN.md](docs/forum-complaint-research.zh-CN.md)

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
  --module relationship-state `
  --module natural-measurement `
  --module embodied-emotion `
  --module vocal-rhythm `
  --strict-continuity `
  --review `
  --context examples/story-ledger.md `
  --task "写下一场戏，保持林乔的听觉代价设定，不要提前解决冲突。"
```

`--review` 是长文友好的精简审查，只自动加入：

- `editor-loop`：先生成，再以挑剔编辑视角诊断，局部重写，最后定稿
- `ai-trace-rubric`：从认知平滑、表达泛化、情感平面、节奏单调、上下文漂移、节拍桥薄弱、关系重置、虚假精确、文化真空、过度干净、结论成瘾等维度评分

`--deep-review` 会在精简审查上加入：

- `relationship-stance-audit`：检查说话人、听话人、被提及第三方之间的关系立场、秘密和信息权限
- `cliche-phrase-audit`：检查高频套话、塑料身体动作、空洞情绪标签和万能转场
- `formulaic-structure-audit`：检查三连式、双向对举、连续“比”比较和每段都收束得太完整的公式结构
- `surface-pattern-audit`：按文体检查意义拔高、模糊归因、假范围、词汇轮换、排版套路和装饰性连续比较
- `prose-progress-audit`：检查每段是否真的推进了事实、关系、证据、动作或压力
- `natural-measurement`：小说、网文和自媒体中检查不合语境的假精确数字

`--strict-continuity` 会自动加入：

- `spatial-blocking`：座位、站位、前后左右、移动过渡检查
- `occupancy-capacity`：物理资源容量、形态、占用者和转换过渡检查
- `appearance-prop-continuity`：服装、鞋子、道具、伤口和身体状态检查

需要成稿物理状态矛盾审查时使用 `audit --profile physical`。

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
