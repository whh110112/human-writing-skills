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
会使用不同容忍度。小说、网文和自媒体还会检查密集比喻（`IMG001`）、连续四个
以上短段（`PARA001`）、履历式资料倾倒（`INFO001`）以及动作后重复解释同一情绪
（`EMO002`）；这些规则不会套到论文和新闻上。代码、链接和 Markdown 引文不会
参与扫描。新增规则还会定位电影式开场堆料（`OPEN002`）、反复使用模糊的内心
自我解释（`EMO003`）以及多章连续从天气、光线和穿着重新开场（`RESET001`）。

分数是透明、可重复的编辑启发式，不是 AI 作者身份的证据。每个命中都需要结合
语境人工判断，有意保留的规则可用 `--allow` 放行。`pipeline` 会在模型审稿文件前
自动生成 `00-pattern-lint.md` 和 JSON。
