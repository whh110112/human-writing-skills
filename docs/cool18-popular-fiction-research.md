# Cool18 Popular-Fiction Research

## Scope and Limits

This study reviewed the public Cool18 Books section on 2026-07-17, including the
[current popular-post ranking](https://www.cool18.com/bbs4/index.php?app=forum&act=hot),
public thread pages, and the site's
[2025 popular-fiction retrospective](https://www.cool18.com/bbs4/index.php?act=threadview&app=forum&tid=14527517).
It records rankings, page structure, chapter statistics, and short craft analysis;
it does not store or reproduce novel text.

Read counts measure attention, not prose quality. The site offers AI voting and
filtering, but an unmarked post or a zero vote count does not prove authorship. The
project therefore uses site labels only as weak evidence and treats deterministic
patterns as editing signals, never authorship detection.

## Positive Craft Signals

- Titles, premise, relationship, and opening establish a clear reader promise.
- Familiar settings carry social, material, or relationship pressure before lore expands.
- Dialogue changes permission, knowledge, debt, risk, rank, trust, or commitment.
- Chapters pass forward a live object, secret, cost, promise, injury, or relationship shift.
- Emotional suspense asks what a character will accept, refuse, hide, lose, or retaliate against.
- Roughness is acceptable when reference, blocking, consequence, and scene pressure stay clear.

The site's annual retrospective summarizes recurring popularity through fluency,
plot fluctuation, and sustained updates. That is a site-specific reader observation,
not permission to ignore logic, physical continuity, or relationship state.

## Negative Controls

High-read samples were excluded from positive technique extraction when they relied on:

- exact clock, named location, weather or colored light, full outfit, scent, and
  generalized feeling before the first consequential action;
- repeated chapter openings that rebuild scenery while dropping prior residue;
- recurring vague self-interpretation such as unexplained feelings and symmetrical
  self-corrections;
- dense metaphor and sensation without a changed choice, permission, risk, or relationship;
- unrelated last-minute threats used to manufacture a hook.

Popularity can coexist with these weaknesses. The project extracts transferable
narrative mechanics rather than copying surface diction from ranked work.

## Project Mapping

| Finding | Implementation |
| --- | --- |
| Chapters provide atmosphere without payoff | `chapter-momentum-audit`, optional `momentum` profile |
| Cinematic setup bundle | `scene-entry-audit`, `OPEN002` |
| Repeated vague introspection | `EMO003` |
| Chapters repeatedly restart from scenery | `RESET001` |
| Multi-chapter audit without prior context | `momentum` remains separate from context-gated `serial` |

`momentum` is excluded from default `full`, `--review`, and `--deep-review` prompts.
`pipeline --auto` selects it only for two or more chapter headings or repeated
continuation markers. Cinematic entry issues remain in the separate `texture` profile.
