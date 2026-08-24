---
name: human-writing-skills
description: Advanced multilingual AI humanizer for natural rewriting, fiction editing, long-form audit, chunked manuscript review, writing style unification, and character consistency. Humanize AI text, remove robotic AI tone, edit fiction and novels, continue webnovel chapters, proofread writing, and audit story continuity, character voice, dialogue register, scene geography, relationships, numbers, citations, and source meaning. Use for AI writing cleanup, style matching from supplied samples, long-context fiction, essays, news, official, academic, legal, and technical prose. Trigger on humanize AI text, de-AI writing, natural rewriting, novel writing assistant, story consistency checker, scene ending audit, reflective ending, long-form style consistency, chunked audit, style consistency review, character consistency audit, 增强版去 AI 写作 Skill、高级 AI 写作工具、去AI味、去AI写作、消除AI腔、AI人性化改写、AI文本润色、AI文章润色、小说润色、小说续写、AI式结尾、生硬结尾审查、无意义升华、长文一致性、长篇审查、分块审查、文风统一、统一文风、人物设定统一、人物一致性审查、跨章一致性、小说审查、报告审查、人物口吻、方言语域、战力设定、场景空间审查.
---

# Advanced Human Writing & AI Humanizer

Humanize AI-shaped text, write or continue genre-aware prose, and audit long-form
continuity without flattening a specific voice. Use the smallest set of modules
that covers the task. Keep project facts, prior chapters, rewrite originals, and
continuity ledgers separate from optional style references.

## Capability Layers

- The `humanwriting/` Python package is executable. Its CLI deterministically
  compiles prompts, locates recurring text patterns, calculates diagnostics,
  previews conservative fixes, checks protected content, and writes staged audits.
- The Markdown files under `skills/` are model-executed writing and editorial
  modules. They are selected by the compiler and are intentionally not pretending
  to be deterministic NLP algorithms.
- A normal installation includes both layers. Verify the executable layer with
  `human-writing-skills list --kind module` and run a real draft through `lint`,
  `fix`, `verify`, or `pipeline` rather than judging the package from `SKILL.md` alone.

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
   `narrative-naturalness-audit` is reserved for deep or explicit AI-trace review of
   narrative prose; it is not loaded for ordinary quick humanization or serious documents.
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
   `ending`, `texture`, `fidelity`, `preservation`, examples, and `sources` separate from the default audit. Activate them explicitly
   or through `pipeline --auto`. `serial` requires context, `recurrence` requires at
   least three chapters, `fidelity` requires `--original`, `preservation` requires
   both explicit selection and `--original`, examples require an explicit request,
   and `sources` requires both a serious document and `--source`.
8. For a book-length manuscript or large report, use `chunk-audit` instead of placing
   the whole draft in one prompt. Supply `--outline` or `--context` for authoritative
   character or report rules. Read `docs/long-form-consistency.md` only for this workflow.

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
human-writing-skills audit --draft chapter.md --document-type fiction --profile ending
human-writing-skills audit --draft paper.md --document-type academic-paper --source study.md --profile sources
human-writing-skills audit --draft revised.md --original original.md --profile fidelity
human-writing-skills audit --draft revised.md --original original.md --profile preservation
human-writing-skills pipeline --draft chapter.md --context ledger.md --auto --with-stats --output-dir audit
human-writing-skills chunk-audit --draft full-novel.md --style fiction --outline outline.md --output-dir novel-audit
human-writing-skills lint --draft chapter.md --style fiction
human-writing-skills stats --draft chapter.md --style fiction
human-writing-skills fix --draft chapter.md --preview
human-writing-skills verify --source original.md --candidate revised.md
```

Read `README.md` or `README.zh-CN.md` for user-facing guidance. Read files under
`docs/` only for the workflow being used. Do not claim detector evasion or infer
authorship from stylistic patterns; frame results as editing evidence.
