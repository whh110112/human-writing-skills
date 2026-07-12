# Multi-Stage Audit Pipeline

Loading every audit rule at once increases coverage, but it does not guarantee deeper checking. A crowded prompt can make a model skip dimensions, mix output contracts, or spend context on repeated instructions.

The project keeps three complementary modes:

| Mode | Purpose |
| --- | --- |
| `build --review` | Compact editing and AI-trace guidance during generation |
| `build --deep-review` | Complete self-review when context is plentiful |
| `pipeline` | Independent, single-purpose passes over the same draft |

## Complete Pipeline

```powershell
human-writing-skills pipeline `
  --draft my-chapter.md `
  --context my-novel-ledger.md `
  --output-dir chapter-audit
```

It writes stages for logic, character consistency, relationship stance, physical continuity, AI traces, number sense, and proofreading.

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
- `physical` for space, movement, appearance, or prop cues
- `numbers` for exact numbers with units
- `style-match` only when `--reference` or `--reference-style` explicitly activates it

The generated manifest records why every stage was selected or skipped. Detection is a conservative text heuristic, not complete story understanding; explicitly select stages for important chapters.

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

## Recommended Order

```text
pattern lint -> logic -> character/relationship -> physical -> AI trace -> style match -> numbers -> proofreading
```

After structural changes, re-run affected downstream stages.

`pipeline` writes prompt files only. It does not call Chatbox or another model and does not merge model reports, which keeps it portable across desktop tools, local models, and API workflows.
