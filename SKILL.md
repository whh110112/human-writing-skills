---
name: human-writing-skills
description: Humanize, write, rewrite, or audit natural Chinese and English prose with genre-aware voice, long-form continuity, semantic fidelity to supplied originals, character-fit dialogue, physical and relationship consistency, deterministic AI-tone pattern linting, optional style statistics, and source-grounded serious writing. Use for fiction, webnovels, essays, news, self-media, academic prose, chapter continuation, proofreading, supplied-sample style calibration, and detailed manuscript review.
---

# Advanced Human Writing Skills

Use the smallest set of modules that covers the task. Keep project facts, prior
chapters, and continuity ledgers separate from optional style references.

## Workflow

1. Select one base style from `skills/`: `fiction`, `webnovel`, `argumentative`,
   `news-report`, `self-media`, or `academic-paper`.
2. Read only the relevant modules. Add continuity, spatial, relationship, number,
   dialogue, world, process, salience, recurrence, source, rhythm, or AI-trace modules
   when the text actually needs them.
3. Treat user facts and `--context` as authoritative. Never borrow facts from a
   style sample. When `--original` is supplied for a rewrite, activate
   `rewrite-fidelity` and preserve meaning without preserving awkward wording.
4. Activate `reference-style-alignment` only when the user supplies reference
   material, gives an explicit style direction, or directly asks to match a style.
5. Treat `--source` as factual evidence only. Activate `source-grounding` only for
   serious academic, news, legal, or technical work with explicit source files.
6. For important revisions, run deterministic `lint`, then independent audit
   profiles, then `verify` protected content against the source. Run `stats` only
   when distributional diagnostics help; use `fix` as a preview before writing.
7. Keep `voice`, `serial`, `world`, `process`, `momentum`, `salience`, `recurrence`,
   `texture`, `fidelity`, and `sources` separate from the default audit. Activate them explicitly
   or through `pipeline --auto`. `serial` requires context, `recurrence` requires at
   least three chapters, `fidelity` requires `--original`, and `sources` requires
   both a serious document and `--source`.

## Commands

```powershell
human-writing-skills build --style fiction --context ledger.md --task "Continue the scene."
human-writing-skills build --style fiction --reference sample.md --task "Match the sample's restrained rhythm."
human-writing-skills build --style self-media --original original.md --task "Rewrite without adding facts."
human-writing-skills audit --draft chapter.md --context ledger.md --profile physical
human-writing-skills audit --draft chapter.md --profile voice
human-writing-skills audit --draft chapter.md --context ledger.md --profile serial
human-writing-skills audit --draft chapters.md --profile momentum
human-writing-skills audit --draft chapters.md --profile recurrence
human-writing-skills audit --draft chapter.md --profile process
human-writing-skills audit --draft paper.md --document-type academic-paper --source study.md --profile sources
human-writing-skills audit --draft revised.md --original original.md --profile fidelity
human-writing-skills pipeline --draft chapter.md --context ledger.md --auto --with-stats --output-dir audit
human-writing-skills lint --draft chapter.md --style fiction
human-writing-skills stats --draft chapter.md --style fiction
human-writing-skills fix --draft chapter.md --preview
human-writing-skills verify --source original.md --candidate revised.md
```

Read `README.md` or `README.zh-CN.md` for user-facing guidance. Read files under
`docs/` only for the workflow being used. Do not claim detector evasion or infer
authorship from stylistic patterns; frame results as editing evidence.
