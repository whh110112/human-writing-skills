# 增强版去 AI 写作 Skill

这是一个面向中文用户的高级 AI 写作工具、去 AI 味工具和长文审校工具。它既能对已有文章进行 AI 文本润色、自然化改写和消除 AI 腔，也能辅助小说、网文、自媒体、新闻、论文、公文与技术文档的撰写和审核，并支持 AI 式结尾审查、生硬结尾审查、长篇审查、分块审查、文风统一、人物设定统一和报告审查。

项目不是只有提示词说明。它同时提供可执行的 Python CLI 和按需加载的写作 Skills：CLI 负责确定性扫描、保守修复、提示词编译、不可改内容校验和分阶段审稿；Skills 负责文体、人物、场景、关系、逻辑与长篇上下文等需要模型判断的编辑任务。

## 适用场景

- 去AI味、去AI写作、消除AI腔、AI人性化改写、AI文章润色和自然语言改写。
- 小说润色、网络小说创作、章节续写、人物对白、文风匹配和长篇上下文一致性检查。
- 检查人物位置、场景空间、衣着道具、关系立场、人物口吻、方言语域、战力能力与世界设定是否前后一致。
- 识别机械排比、不是而是、比较阶梯、虚假精确数字、生硬转场、悬空对白、小标题滥用、漏字和套话密度等常见 AI 写作痕迹。
- 识别场景已经结束后追加的风景渐隐、沉默反思、人生感悟、未来展望与无意义升华；通过最后有效变化和删除测试修复 AI 小说结尾与伪收束。
- 在论文、新闻、法律、公文和技术文本中保护数字、引用、专有名词、结论和来源边界。
- 根据用户明确提供的原文、前文章节或参考资料匹配语言节奏、人物说话方式和场景描写风格；没有参考材料时不会擅自激活。

## 核心能力

1. **自然化改写**：保留原意、事实和有效含混，减少模板化结构与机械句式，而不是简单替换所谓禁用词。
2. **文体区分**：小说强调动作、感官、对白与场景推进；新闻、论文、公文和技术文本强调事实、证据与术语准确性。
3. **长文连续性**：结合人物账本、场景账本、关系状态、物理状态和前文章节，检查人物、位置、服装、道具、能力与剧情衔接。
4. **人物对白一致性**：根据身份、经历、关系、目的、听众和当下场景控制称呼、敬语、语气词、方言、隐瞒与潜台词。
5. **物理世界审核**：使用容量、占用、可达性、移动过程和状态转换等通用规则，识别瞬移、重复占位和缺少过渡的状态变化。
6. **可执行审查**：`lint`、`fix`、`verify`、`stats` 和 `pipeline` 可执行确定性检查与多阶段审稿，不把所有能力都伪装成程序算法。
7. **分块文风统一**：`chunk-audit` 用已认可文风基准和大纲/账本拆分超长小说或报告，检查跨月、跨模型版本的文风、人物对白、术语和章节功能漂移。
8. **结尾功能审查**：`earned-ending-audit` 区分小说、新闻、论文、公文的结尾职责，清理反思式尾句和公式化结论，又不把安静意象或正常总结当成禁词。

## 按需加载

默认只加载完成当前任务所需的最小模块，避免把完整规则库一次塞入上下文。关系、空间、战力、数字、参考文风、长篇复现和严肃文本保护等模块，仅在输入中存在对应证据或用户明确选择时激活。

- 普通快速润色使用 `humanize --mode quick`。
- 需要结构重写、段落推进或深入审稿时使用 `humanize --mode deep`。
- 长篇小说有前文或设定资料时，使用 `--context` 激活连续性能力。
- 只有用户提供原文时才使用 `--original` 保护改写语义。
- 只有用户提供参考文风或明确要求参考某种写法时才使用 `--reference`。
- 只有新闻、论文、公文、法律或技术任务提供来源时才使用 `--source`。

## 常用命令

```powershell
human-writing-skills humanize --draft article.md --style self-media --mode quick
human-writing-skills build --style fiction --context ledger.md --task "续写下一章"
human-writing-skills build --style fiction --reference sample.md --task "参考样文的节奏写新场景"
human-writing-skills audit --draft chapter.md --context ledger.md --profile physical
human-writing-skills audit --draft chapter.md --profile voice
human-writing-skills audit --draft chapter.md --document-type fiction --profile ending
human-writing-skills pipeline --draft chapter.md --context ledger.md --auto --output-dir audit
human-writing-skills chunk-audit --draft full-novel.md --style fiction --outline novel-outline.md --output-dir novel-audit
human-writing-skills lint --draft chapter.md --style fiction
human-writing-skills fix --draft chapter.md --preview
human-writing-skills verify --source original.md --candidate revised.md
```

详细安装、Chatbox 用法、长篇账本模板和完整审稿流程见 `README.zh-CN.md` 与 `docs/`。本项目用于写作与编辑质量改进，不承诺规避检测器，也不根据文字特征判断作者身份。
