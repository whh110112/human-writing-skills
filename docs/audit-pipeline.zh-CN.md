# 多阶段审稿流水线

一次加载所有审查规则能扩大覆盖面，但不保证每一项都检查得更深。规则过多时，模型可能漏项、混用标准，或者把大量上下文花在重复说明上。

本项目同时保留三种方式：

| 方式 | 用途 |
| --- | --- |
| `build --review` | 正文生成时的精简编辑与 AI 痕迹提醒 |
| `build --deep-review` | 上下文充足时的完整生成后自审 |
| `pipeline` | 把同一稿件拆成多个互不干扰的独立审稿阶段 |

## 完整流水线

```powershell
human-writing-skills pipeline `
  --draft my-chapter.md `
  --context my-novel-ledger.md `
  --output-dir chapter-audit
```

默认生成：

1. `logic`：逻辑、时间线、知识来源、动机、规则、资源和后果
2. `character`：人物目标、声音、能力、边界、知识和变化桥梁
3. `relationship`：谁在谁面前提谁、阵营、等级、秘密和信息权限
4. `physical`：位置、容量、触达、服装、道具和伤势
5. `ai-trace`：套话、公式结构、段落无推进和其他 AI 痕迹
6. `numbers`：动作与情绪中的假精确数字
7. `proofread`：错别字、标点、称谓、排版和机械错误

输出目录里的每个 Markdown 都是一份完整但单一职责的提示词。应在新的 Chatbox 会话、独立 API 请求或没有上一阶段聊天记忆的模型会话中分别运行。

## 动态按需加载

```powershell
human-writing-skills pipeline `
  --draft my-chapter.md `
  --context my-novel-ledger.md `
  --auto `
  --output-dir chapter-audit
```

自动模式始终保留：

- `logic`
- `ai-trace`
- `proofread`

然后根据本章内容决定是否追加：

- 有人物行为或声音线索：`character`
- 有对话、等级、阵营、亲密或秘密线索：`relationship`
- 有位置、移动、服装、道具或空间线索：`physical`
- 有带单位的精确数字：`numbers`

`README.md` 清单会记录每个阶段为什么被选择或跳过。自动判断是保守的文本启发式，不理解完整剧情；重要章节应显式指定阶段。

## 显式选择

```powershell
human-writing-skills pipeline `
  --draft my-chapter.md `
  --stage logic `
  --stage character `
  --stage relationship `
  --output-dir chapter-audit
```

`--auto` 和 `--stage` 不能同时使用。

## 推荐执行顺序

先改结构，后改文字：

```text
逻辑 -> 人物/关系 -> 物理 -> AI 痕迹 -> 数字 -> 校对
```

逻辑或剧情结构发生重写后，应重新运行受影响的后续阶段。不要先校对一段随后会被整体删除的文字。

## 边界

`pipeline` 负责生成分阶段提示词文件，不会主动调用 Chatbox 或任何模型，也不会自动合并模型输出。这样可以兼容 Chatbox、Codex、ChatGPT、Claude、本地模型和 API 工作流。
