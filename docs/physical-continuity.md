# Physical Continuity

This guide prevents character teleportation, seat drift, clothing drift, and prop inconsistency in long scenes.

Use it for cars, trains, elevators, booths, bedrooms, hospital rooms, offices, and any narrow space where position matters.

## Recommended Command

Before generation:

```powershell
python -m humanwriting.cli build `
  --style fiction `
  --strict-continuity `
  --review `
  --context examples/vehicle-scene-ledger.md `
  --task "Continue the car argument. Every seat change must have an on-page transition. Keep clothing and props consistent."
```

After a draft already exists:

```powershell
python -m humanwriting.cli audit `
  --draft examples/problem-car-scene-draft.md `
  --context examples/vehicle-scene-ledger.md
```

`--strict-continuity` automatically adds:

- `spatial-blocking`
- `appearance-prop-continuity`
- `physical-continuity-audit`

## What To Track

| Category | Examples |
| --- | --- |
| Position | driver seat, front passenger seat, rear-left, rear-right |
| Facing | forward, toward window, through mirror |
| Reach | wheel, glove box, door handle, nearby person |
| Obstacles | seat belt, console, table, doorway, front seat back |
| Movement gate | stops car, unbuckles, opens door, climbs out, squeezes past |
| Appearance | skirt length, shoes, coat, hair, makeup, injuries |
| Props | phone, bag, letter, weapon, keys, umbrella |

## Rule

If no transition is written, the previous physical state remains true.

That single rule prevents most seat drift, clothing drift, and object drift.

## Why Use `audit`

`build --strict-continuity` is a generation guard. It helps before drafting, but a model may still miss contradictions when reviewing an existing passage.

The `audit` command creates a forensic review prompt. It forces evidence extraction before judgment, then checks:

- front/rear seat drift
- barriers such as soundproof glass or partitions
- impossible reach, touch, handoff, or direct whispering
- shoes, skirt length, coat, injury, and prop drift
- missing movement gates such as stopping, unbuckling, opening a door, or changing seats
