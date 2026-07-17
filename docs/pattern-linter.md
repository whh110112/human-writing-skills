# Deterministic Writing-Pattern Linter

`lint` finds observable editing patterns and reports rule IDs, severity, line,
column, offsets, evidence, and a repair direction.

```powershell
human-writing-skills lint --draft chapter.md --style fiction
human-writing-skills lint --draft report.md --style academic-paper --format json
human-writing-skills lint --draft chapter.md --allow PREC001 --fail-score 35
```

Checks include inflated vocabulary, generic body cues, empty atmosphere, formulaic
contrast, dead transitions, chatbot residue, promotional language, stacked hedging,
false precision, unusually uniform sentence rhythm, and excessive dash density.
For narrative styles it also checks dense comparison clusters (`IMG001`), four-or-more
short-paragraph runs (`PARA001`), biographical detail inventory (`INFO001`), and
action immediately followed by a duplicate emotion gloss (`EMO002`). Genre profiles
suppress these rules for news or academic writing. Code, URLs, and Markdown
quotations are masked.

The score is transparent and deterministic, but it is not evidence of AI
authorship. Review every evidence span in context and allowlist intentional usage.
`pipeline` writes the same preflight as `00-pattern-lint.md` and JSON before its
model-based stages.
