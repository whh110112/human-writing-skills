---
name: human-writing-skills
description: Advanced multilingual human writing and AI humanizer toolkit. Humanize AI text, remove robotic AI tone, rewrite natural prose, edit fiction and novels, continue chapters, and audit story continuity, character voice, dialogue register, dialect and language identity, capability or power state, scene geography, physical state, relationships, numbers, citations, and source meaning. Use for AI writing cleanup, de-AI writing, naturalization, proofreading, style matching from supplied samples, long-context fiction, webnovels, essays, official documents, news, self-media, academic, legal, and technical prose in Chinese, English, Japanese, French, Spanish, Portuguese, Arabic, Latin, and other model-supported languages. Also trigger for requests such as 去AI味、消除AI腔、AI文本润色、小说润色、小说续写、长文一致性、人物口吻、方言语域、战力设定、场景空间审查.
---

# Advanced Human Writing & AI Humanizer

Humanize AI-shaped text, write or continue genre-aware prose, and audit long-form
continuity without flattening a specific voice. Use the smallest set of modules
that covers the task. Keep project facts, prior chapters, rewrite originals, and
continuity ledgers separate from optional style references.

## Quick Humanize Route

- For a supplied draft, use `humanize --mode quick` for surface patterns,
  rewrite fidelity, and voice/ambiguity preservation.
- Use `--mode deep` only when structural repetition, cliches, paragraph stagnation,
  or broad editorial reconstruction needs a separate pass.
- Load `humanize-examples` only after an explicit request or `--with-examples`.
- Do not activate rewrite-preservation modules for unrelated new drafting.

## Workflow

1. Select one base style from `skills/`: `fiction`, `webnovel`, `argumentative`,
   `news-report`, `formal-document`, `self-media`, or `academic-paper`.
2. Read only the relevant modules. Add continuity, spatial, relationship, number,
   dialogue, register, capability, world, process, salience, recurrence, source, rhythm, preservation,
   or AI-trace modules when the text actually needs them.
3. Treat user facts and `--context` as authoritative. Never borrow facts from a
   style sample. When `--original` is supplied for a rewrite, activate
   `rewrite-fidelity` and preserve meaning without preserving awkward wording.
   In fiction and webnovels, do not let time/place mini-headings replace scene bridges.
4. Activate `reference-style-alignment` only when the user supplies reference
   material, gives an explicit style direction, or directly asks to match a style.
5. Treat `--source` as factual evidence only. Activate `source-grounding` only for
   serious academic, formal, news, legal, or technical work with explicit source files.
6. For important revisions, run deterministic `lint`, then independent audit
   profiles, then `verify` protected content against the source. Run `stats` only
   when distributional diagnostics help; use `fix` as a preview before writing.
7. Keep `voice`, `serial`, `world`, `process`, `momentum`, `salience`, `recurrence`,
   `texture`, `fidelity`, `preservation`, examples, and `sources` separate from the default audit. Activate them explicitly
   or through `pipeline --auto`. `serial` requires context, `recurrence` requires at
   least three chapters, `fidelity` requires `--original`, `preservation` requires
   both explicit selection and `--original`, examples require an explicit request,
   and `sources` requires both a serious document and `--source`.

## Commands

```powershell
human-writing-skills build --style fiction --context ledger.md --task "Continue the scene."
human-writing-skills humanize --draft chapter.md --style fiction --mode quick
human-writing-skills humanize --draft article.md --style self-media --mode deep --with-examples
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
human-writing-skills audit --draft revised.md --original original.md --profile preservation
human-writing-skills pipeline --draft chapter.md --context ledger.md --auto --with-stats --output-dir audit
human-writing-skills lint --draft chapter.md --style fiction
human-writing-skills stats --draft chapter.md --style fiction
human-writing-skills fix --draft chapter.md --preview
human-writing-skills verify --source original.md --candidate revised.md
```

Read `README.md` or `README.zh-CN.md` for user-facing guidance. Read files under
`docs/` only for the workflow being used. Do not claim detector evasion or infer
authorship from stylistic patterns; frame results as editing evidence.
