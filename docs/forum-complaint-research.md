# Common Writing Problems and Repair Map

This page turns recurring structural, expressive, and continuity problems in
long-form writing into executable audit modules.

## Design Principles

- Prioritize problems that recur across genres instead of hard-coding one sample.
- Treat phrases and sentence shapes as signals, not automatic deletion rules.
- Let genre, character voice, context, and intent decide whether wording should stay.
- Repair evidence, action, rhythm, and state change instead of merely swapping synonyms.

## Common Complaints

| Reader Complaint | Deeper Cause | Recommended Modules |
| --- | --- | --- |
| Too smooth, too complete, template-shaped | Paragraphs are symmetrical and every thought resolves cleanly | `formulaic-structure-audit`, `controlled-drift`, `vocal-rhythm` |
| Plastic stock phrases | Cliches replace observation, action, and proof | `cliche-phrase-audit`, `embodied-emotion`, `cultural-anchors` |
| Polished but hollow | Paragraphs restate the same premise without a new state change | `prose-progress-audit`, `editor-loop` |
| Big emotion, low realism | The draft names feelings without body, action, contradiction, or consequence | `embodied-emotion`, `relationship-state` |
| Dead transitions | Connective phrases replace causality, objects, action, or point of view | `narrative-bridges`, `formulaic-structure-audit` |
| Cultural vacuum | The prose lacks era, place, material detail, and community language | `cultural-anchors` |
| Long-form drift | Facts, relationships, space, props, and hooks are not tracked | `relationship-state`, `spatial-blocking`, `physical-continuity-audit` |
| False precision | Human perception is written like measurement data | `natural-measurement` |

## How the New Modules Help

### Cliche Phrase Audit

`cliche-phrase-audit` checks for stock fate language, generic body cues,
decorative emotional labels, dead transitions, and common English AI-slop phrases.

The repair is not synonym swapping. Replace the weak phrase with a visible action,
specific object, local sensory fact, attributed evidence, character-specific verbal
habit, or causal bridge.

### Formulaic Structure Audit

`formulaic-structure-audit` checks for overused triplets, symmetrical contrasts,
identical paragraph cadence, and paragraphs that close too neatly.

The repair is purposeful asymmetry: keep necessary order, vary paragraph function,
and let some pressure carry into the next beat.

### Prose Progress Audit

`prose-progress-audit` asks what became newly true in every paragraph. If two
neighboring paragraphs reduce to the same summary, cut, merge, replace with
evidence, or convert explanation into action.

## Recommended Commands

Use `--deep-review` for the complete structure-and-expression audit set; use compact `--review` for long-form continuation:

```powershell
python -m humanwriting.cli build `
  --style fiction `
  --deep-review `
  --strict-continuity `
  --context examples/story-ledger.md `
  --task "Write the next scene. Avoid stock phrases and formulaic paragraph shapes."
```

Audit an existing draft:

```powershell
python -m humanwriting.cli audit `
  --draft examples/problem-car-scene-draft.md `
  --context examples/vehicle-scene-ledger.md `
  --profile full `
  --profile numbers
```

AI taste is not only a word-list problem. It emerges when structure, evidence,
rhythm, voice, and context maintenance fall out of balance.
