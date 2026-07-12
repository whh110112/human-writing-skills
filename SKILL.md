---
name: human-writing-skills
description: Write, rewrite, or audit natural, genre-aware prose with long-form continuity, explicit reference-style matching, physical and relationship consistency, deterministic AI-pattern linting, and protected fact verification. Use for fiction, webnovels, essays, news, self-media, academic prose, chapter continuation, style calibration from supplied samples, and detailed manuscript review.
---

# Human Writing Skills

Use the smallest set of modules that covers the task. Keep project facts, prior
chapters, and continuity ledgers separate from optional style references.

## Workflow

1. Select one base style from `skills/`: `fiction`, `webnovel`, `argumentative`,
   `news-report`, `self-media`, or `academic-paper`.
2. Read only the relevant modules. Add continuity, spatial, relationship, number,
   rhythm, or AI-trace modules when the text actually needs them.
3. Treat user facts and `--context` as authoritative. Never borrow facts from a
   style sample.
4. Activate `reference-style-alignment` only when the user supplies reference
   material, gives an explicit style direction, or directly asks to match a style.
5. For important revisions, run deterministic `lint`, then independent audit
   profiles, then `verify` protected content against the source.

## Commands

```powershell
human-writing-skills build --style fiction --context ledger.md --task "Continue the scene."
human-writing-skills build --style fiction --reference sample.md --task "Match the sample's restrained rhythm."
human-writing-skills audit --draft chapter.md --context ledger.md --profile physical
human-writing-skills pipeline --draft chapter.md --context ledger.md --auto --output-dir audit
human-writing-skills lint --draft chapter.md --style fiction
human-writing-skills verify --source original.md --candidate revised.md
```

Read `README.md` or `README.zh-CN.md` for user-facing guidance. Read files under
`docs/` only for the workflow being used. Do not claim detector evasion or infer
authorship from stylistic patterns; frame results as editing evidence.
