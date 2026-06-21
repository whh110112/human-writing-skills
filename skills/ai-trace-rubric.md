# AI Trace Rubric

## Aim

Provide a qualitative scoring pass that identifies where a draft still feels machine-shaped.

Score each dimension from 0 to 3:

- 0: not a problem
- 1: mild issue
- 2: visible issue
- 3: dominant issue

## Dimensions

| Dimension | Warning Sign | Repair Direction |
| --- | --- | --- |
| Cognitive smoothness | Every transition is complete and safe | Add controlled drift, doubt, or fragile inference |
| Generic diction | Sentences could fit any topic | Replace with object, place, action, or speaker-specific detail |
| Emotional flatness | Emotion is named but not embodied | Add action, body signal, sensory distortion, contradiction |
| Rhythm monotony | Sentences move at one speed | Add breath variation, short brakes, altered cadence |
| Context drift | Facts, stakes, or timeline blur | Update and obey the continuity ledger |
| Weak beat bridge | Paragraphs or scenes sit beside each other instead of causing each other | Reconnect residue, micro-turn, proof detail, and exit pressure |
| Relationship reset | Trust, boundaries, secrets, or leverage reset after charged scenes | Track who knows, wants, hides, owes, refuses, and can withdraw |
| Cultural vacuum | No era, place, class, or community signal | Add one precise cultural anchor |
| Over-clean prose | No hesitation, revision, roughness, or pressure | Add genre-appropriate imperfection |
| Closure addiction | Every thought resolves neatly | Leave one productive open question or unresolved pressure |

## Output Format

```text
AI Trace Review
- Cognitive smoothness: 2 -- transitions over-explain cause and effect.
- Emotional flatness: 1 -- one embodied detail is present, but the final sentence summarizes.
- Highest-priority repair: replace the final explanation with action.
```

## Revision Check

Never optimize all dimensions to zero if the genre needs friction. The goal is a convincing human voice, not sterile perfection.
