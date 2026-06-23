# Physical Continuity Audit Skill

## Aim

Run a hard continuity check for spatial position, movement, clothing, props, and body state before final output.

For already-written drafts, prefer `forensic-physical-audit`. This skill is still useful as a final pass, but forensic review is stricter because it requires evidence tables before judgment.

## Audit Procedure

1. Extract all physical facts from the draft:
   - position
   - direction/facing
   - clothing and shoes
   - carried objects
   - injuries and body constraints
   - doors, seats, exits, furniture, vehicle layout
   - barriers such as soundproof glass, partitions, locked doors, seat backs, seat belts
   - reach/contact actions such as touching, grabbing, passing objects, whispering directly, or close physical contact
   - occupancy/capacity claims about who or what shares a physical resource

2. Compare them against the ledger:
   - fixed physical facts
   - occupancy and capacity table
   - current blocking table
   - appearance and prop table
   - movement log

3. Flag contradictions:
   - unexplained seat change
   - over-occupied or mode-ambiguous physical resource
   - impossible reach or eye contact
   - contact across a barrier without a workaround
   - clothing or footwear drift
   - object appears/disappears
   - injury or constraint vanishes
   - doorway/path blocked but used freely

4. Repair locally:
   - add a movement beat
   - revise the position
   - update the ledger if a real change occurred
   - remove impossible action

## Output Format When Asked For Audit Notes

```text
Physical Continuity Audit
- Blocking: pass/fail
- Appearance: pass/fail
- Props: pass/fail
- Movement gates: pass/fail
- Barriers and reach/contact: pass/fail
- Repairs made:
  - ...
```

## Silent Mode

If the user asks only for prose, perform the audit silently and return the corrected passage.
