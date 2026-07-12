# 受保护内容校验

润色和改写可能悄悄改掉百分比、引文编号、公式、链接、代码、原话或指定术语。
保护分成两步：

1. 审稿时加入 `--protect-content` 或 `--protect-term`，让模型收到保护清单；发现
   疑似错误只能报告，不能自行改数值。
2. 改写完成后运行 `verify`，对原文和候选稿做确定性比较。

```powershell
human-writing-skills audit --draft original.md --protect-content --protect-term "星港计划"
human-writing-skills verify --source original.md --candidate revised.md --protect-term "星港计划"
```

退出码 `0` 表示原文保护项仍然存在；退出码 `1` 表示至少一项缺失或发生改变。
候选稿新增的数字等内容会单独列出。这个工具只检查文字是否被改，不判断原始事实
本身是否正确。
