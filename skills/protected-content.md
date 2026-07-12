# Protected Content

## Aim

Preserve facts and exact spans that stylistic rewriting must not change.

## Protected Categories

- Numbers, dates, percentages, prices, measurements, dosages, and identifiers
- Citations, citation keys, footnote markers, equations, and symbols
- URLs, file paths, code spans, and fenced code blocks
- Directly quoted source passages and attributed statements
- User-specified names, terminology, product names, legal language, and house terms

## Rules

- Do not silently normalize, translate, shorten, reorder, or "improve" protected content.
- Preserve occurrence counts when repetition carries factual or structural meaning.
- If grammar requires a change around a protected span, rewrite the surrounding sentence.
- If a protected item appears wrong, flag it for the user; do not correct it without authority.
- Do not invent a missing citation, statistic, result, source, partner, or quotation.
- After rewriting, compare the source and candidate mechanically. A fluent rewrite that
  changes a result or citation is a failed rewrite.

## Output Check

```text
Protected Content Check
- Preserved exactly:
- Missing or changed:
- Added factual-looking content requiring verification:
- Rewrite status: pass / fail
```
