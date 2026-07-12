# 确定性写作痕迹扫描

`lint` 针对可观察的文字模式给出规则编号、严重程度、行列、字符区间、原文证据和
修改方向。

```powershell
human-writing-skills lint --draft chapter.md --style fiction
human-writing-skills lint --draft report.md --style academic-paper --format json
human-writing-skills lint --draft chapter.md --allow PREC001 --fail-score 35
```

检查内容包括夸大词汇、万能身体动作、空洞氛围、公式化转折、死转场、聊天助手
残留、宣传腔、叠加模糊词、假精确数字、句长过度整齐和破折号密度。新闻与论文
会使用不同容忍度；代码、链接和 Markdown 引文不会参与扫描。

分数是透明、可重复的编辑启发式，不是 AI 作者身份的证据。每个命中都需要结合
语境人工判断，有意保留的规则可用 `--allow` 放行。`pipeline` 会在模型审稿文件前
自动生成 `00-pattern-lint.md` 和 JSON。
