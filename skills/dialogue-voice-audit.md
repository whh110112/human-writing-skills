# Character-Fit Dialogue

## Aim

Generate and audit dialogue that belongs to this character in this situation.
Keep speakers distinguishable without reducing a profession, class, region, or
temperament to a catchphrase.

## Activation Gate

Use in drafting only when the task explicitly requests dialogue, negotiation,
interview, interrogation, argument, meeting, or another speech-centered scene.
Use in review when the draft contains sustained dialogue or the user selects the
`voice` profile. Do not load for narration-only passages or generic proofreading.

## Evidence Hierarchy

Build from strongest to weakest evidence:

1. Explicit character sheets, continuity ledger, prior chapters, and user instructions.
2. Repeated behavior and speech already established on the page.
3. The current scene's goal, audience, pressure, knowledge, and power balance.
4. Role or cultural priors only as tentative constraints, never as proof of voice.

Do not infer speech style directly from occupation, status, class, region, or one
temperament label. These factors may shape knowledge, incentives, duties, risks,
social options, and code-switching pressure, but they do not define personality.

## Speaker Model

For each important speaker, record only scene-relevant dimensions:

- stable baseline: diction, directness, abstraction, turn length, politeness,
  humor, profanity, titles, and taboo wording
- response habits: answer, evade, counterquestion, bargain, teach, test, flatter,
  threaten, joke, quote, correct, or stay silent
- disclosure habits: what is stated, implied, coded, delayed, or never named
- competence boundary: what the person can know, explain, notice, or misunderstand
- role constraints: duties, institutional incentives, dependencies, liabilities,
  and what outcome counts as success
- audience shift: how the person changes with superiors, subordinates, intimates,
  strangers, rivals, witnesses, or possible overhearers

Treat traits as tendencies, not quotas. A blunt person can rehearse one elegant
sentence; a restrained person can speak plainly under urgency. Repeated departure
needs a visible reason.

## Scene Speech Contract

Before writing or judging the exchange, identify:

```text
speaker -> listener / audience
topic -> why it matters now
speaker goal -> desired listener action or belief
speaker constraint -> what cannot be admitted, promised, or understood
tactic -> wording and silence chosen for this turn
result -> what changes in knowledge, leverage, permission, risk, or emotion
```

The declared topic is not always the real transaction. A practical meeting should
reflect the parties' actual incentives and constraints, but it may detour when the
scene gives a motive such as testing, stalling, face-saving, seduction, intimidation,
misunderstanding, or concealment.

## Drafting Mode

When this file is loaded as a `Technique Module`:

1. Build a compact speaker model and scene speech contract before drafting.
2. Give each turn a purpose and make it respond to the preceding turn.
3. Let expertise appear through what a speaker asks, notices, refuses, corrects,
   or treats as obvious, not through an exposition dump.
4. Keep vocabulary and syntax near the speaker's baseline while allowing motivated
   code-switching for audience, pressure, performance, quotation, or strategy.
5. Make important dialogue transact: alter knowledge, leverage, permission, risk,
   commitment, trust, or the next available action.
6. Do not display the hidden model unless the user asks for notes.

## Audit Mode

When this file is loaded as an `Audit Module`:

1. Extract speaker models and the scene speech contract from evidence.
2. Map representative turns as `goal -> tactic -> wording -> listener update`.
3. Remove labels from several lines and test whether they remain attributable.
4. Flag only evidence-backed failures:
   - interchangeable speakers or narrator-shaped exposition
   - topic or incentive drift without a scene motive
   - knowledge, competence, or institutional-constraint mismatch
   - a reply that ignores the preceding turn
   - unearned register, politeness, directness, dialect, or profanity shift
   - speech incompatible with the current audience, power balance, or emotional load
   - personality reduced to one repeated verbal tic or occupational stereotype
5. Test every deviation for a change gate: audience adaptation, deception,
   performance, quotation, sarcasm, rehearsal, stress, intoxication, panic, intimacy,
   status change, new evidence, or deliberate loss of control.
6. Repair the smallest unit: tactic, wording, address form, omitted fact, silence,
   listener reaction, or one short change-gate beat.

## Output

```text
Character-Fit Dialogue Audit
- Speaker model and evidence source:
- Scene speech contract:
- Turn or line:
- Conflict: baseline / goal / topic / knowledge / role constraint / audience / response
- Confirmed mismatch or uncertain inference:
- Valid change gate, if any:
- Minimal repair and insertion point:
```

Do not invent dialect, jargon, or verbal tics merely to make speakers different.
Do not rewrite a plausible individual into a generic representative of their job.
