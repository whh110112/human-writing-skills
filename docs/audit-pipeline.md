# Multi-Stage Audit Pipeline

Loading every audit rule at once increases coverage, but it does not guarantee deeper checking. A crowded prompt can make a model skip dimensions, mix output contracts, or spend context on repeated instructions.

The project keeps three complementary modes:

| Mode | Purpose |
| --- | --- |
| `build --review` | Compact editing and AI-trace guidance during generation |
| `build --deep-review` | Expanded legacy self-review; optional narrative modules remain explicit |
| `pipeline` | Independent, single-purpose passes over the same draft |

## Complete Pipeline

```powershell
human-writing-skills pipeline `
  --draft my-chapter.md `
  --context my-novel-ledger.md `
  --output-dir chapter-audit
```

It writes the established broad stages for logic, character consistency, relationship
stance, physical continuity, AI traces, number sense, and proofreading. The higher-cost
`voice`, `serial`, `world`, `process`, `momentum`, `salience`, `recurrence`,
`texture`, and `sources` stages stay out unless explicitly selected or detected by
`--auto`.

It also writes `00-pattern-lint.md` and JSON as a deterministic preflight. These
files contain evidence locations and a transparent editing score; they do not
claim to identify the author.

Run every generated Markdown prompt in a fresh Chatbox conversation, independent API request, or model session without prior stage memory.

## Dynamic Selection

```powershell
human-writing-skills pipeline `
  --draft my-chapter.md `
  --context my-novel-ledger.md `
  --auto `
  --output-dir chapter-audit
```

Automatic mode always keeps `logic`, `ai-trace`, and `proofread`. It adds:

- `character` for character-action or voice cues
- `relationship` for dialogue, hierarchy, faction, intimacy, or secrecy cues
- `voice` for sustained attributed dialogue; supplied context also permits shorter attributed exchanges
- `serial` only when prior context is supplied and the draft is narrative
- `world` for explicit era, world-rule, technology-system, or speculative-setting cues
- `process` for sustained consequential process or process-to-result cues
- `momentum` only for a multi-chapter draft or repeated continuation structure
- `salience` only for narrative drafts with at least 4,000 characters and 12 paragraphs
- `recurrence` only for three or more chapter headings
- `physical` for space, movement, appearance, or prop cues
- `texture` for cinematic opening stacks, formulaic introspection, clustered imagery,
  detail inventory, fragment runs, or show-then-gloss cues
- `numbers` for exact numbers with units
- `style-match` only when `--reference` or `--reference-style` explicitly activates it
- `sources` only when factual source files and a serious document type are both present

The `voice` stage checks stable baseline, current goal, knowledge and role constraints,
audience, response linkage, motivated register shifts, and whether pressure-bearing
turns receive verbal, physical, silent, interrupted, or deferred uptake without
equating occupation with personality. The generated manifest records why every stage was selected or
skipped. Detection is a conservative text heuristic, not complete story understanding;
explicitly select stages for important chapters.

## Explicit Stages

```powershell
human-writing-skills pipeline `
  --draft my-chapter.md `
  --stage logic `
  --stage character `
  --stage relationship `
  --output-dir chapter-audit
```

`--auto` and `--stage` are mutually exclusive.

`--stage style-match` is rejected unless reference material or an explicit style
direction is supplied. Only that stage receives the reference text.

`--stage serial` is rejected unless `--context` supplies prior chapters or a
continuity ledger.

`--stage sources` is rejected unless `--source` supplies factual evidence and the
draft is academic, news, legal, or technical. Source files enter only that stage;
they do not become style references or fiction context.

## Recommended Order

```text
pattern lint -> logic -> character/relationship/voice/serial/world/process/momentum -> salience/recurrence -> physical -> AI trace/texture -> style match -> numbers -> sources -> proofreading
```

After structural changes, re-run affected downstream stages.

`pipeline` writes prompt files only. It does not call Chatbox or another model and does not merge model reports, which keeps it portable across desktop tools, local models, and API workflows.
