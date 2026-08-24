# Deterministic Writing-Pattern Linter

`lint` finds observable editing patterns and reports rule IDs, severity, line,
column, offsets, evidence, and a repair direction.

```powershell
human-writing-skills lint --draft chapter.md --style fiction
human-writing-skills lint --draft report.md --style academic-paper --format json
human-writing-skills lint --draft chapter.md --allow PREC001 --fail-score 35
```

Checks include inflated vocabulary, generic body cues, empty atmosphere, formulaic
contrast, dead transitions, chatbot residue, promotional language, stacked hedging,
false precision, vague attribution, false ranges, synonym cycling, formatting habits,
uniform sentence rhythm, and excessive dash density. `STR001` covers both not-X/is-Y
and is-X/not-Y frames. Two valid Chinese `比` clauses trigger medium `STR002`; three
or more trigger high `STR004` outside academic and news styles. `STR003` escalates
when contrast frames recur densely across a passage. This is contextual review, not
automatic deletion. `SYN001` reports high-confidence omission symptoms where a
connector or function word is stranded at sentence end; the model-based proofread
pass handles ambiguous missing constituents through predicate slots, parallel clauses,
and reference resolution.
For narrative styles it also checks dense comparison clusters (`IMG001`), four-or-more
short-paragraph runs (`PARA001`), biographical detail inventory (`INFO001`), and
action immediately followed by a duplicate emotion gloss (`EMO002`). It also checks
cinematic opening bundles (`OPEN002`), repeated vague introspection
(`EMO003`), and repeated chapter scenic resets (`RESET001`). Genre profiles suppress
these rules for news or academic writing. Code, URLs, and Markdown
quotations are masked.

For `fiction` and `webnovel`, `END001` inspects only scene or document exits. It flags
a terminal suffix when several cues combine into a reflective bookend: scenery or
time dissolves, staged stillness, explicit reflection, and thematic summation after
the last meaningful change. One quiet image or reflective sentence is not enough by
itself unless it uses a strong stock-reflection frame. The repair direction is a
deletion test, not replacement with a cliffhanger.

Additional surface families include significance inflation (`SIGN001`), vague
attribution (`ATTR001`), formulaic challenge closures (`CHALLENGE001`), elaborate
English copulas (`COPULA001`), decorative participles (`ING001`), false-range density
(`RANGE001`), inflated lexical clusters (`LEX003`), narrative synonym cycling
(`ALIAS001`), and repeated formatting templates (`FORMAT001`-`FORMAT003`). Most are
density-based so one justified use does not become a ban.

For `fiction` and `webnovel`, `HEAD001` flags unrequested Markdown or standalone-bold
mini-headings inside narrative flow. `HEAD002` flags standalone time cards in Chinese,
English, Japanese, French, Spanish, Portuguese, Arabic, and Latin. A work title and
real chapter heading are preserved; news, academic, argumentative, and self-media
section headings are outside these rules. The repair must restore a prose bridge from
prior residue through elapsed change to the first new action. Use an allowlist for an
explicit log, dossier, epistolary, screenplay, or titled-section form.

These are misuse checks, not banned characters. Keep factual correction, legal
exclusion, source-based comparison, character rebuttal, and intentional fragments.
Repair the information path instead of mechanically replacing a connective.

The score is transparent and deterministic, but it is not evidence of AI
authorship. Review every evidence span in context and allowlist intentional usage.
`pipeline` writes the same preflight as `00-pattern-lint.md` and JSON before its
model-based stages.

For optional distributional statistics and conservative mechanical fixes, see
[editing-tools.md](editing-tools.md).
