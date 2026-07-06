# Human Writing Skills

> Reusable writing `SKILLS` for AI agents that need natural prose, genre-aware style, and long-form continuity.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](pyproject.toml)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](pyproject.toml)

[中文说明](README.zh-CN.md) | English

Human Writing Skills is an open-source skill pack and lightweight prompt compiler for AI-assisted writing.

It helps a writing agent move away from generic, template-shaped output and toward prose that has intention, texture, continuity, and genre discipline. The project is especially useful for long-form generation, where characters, settings, arguments, facts, and unresolved threads often drift after several passages.

The goal is not deception. The goal is better writing: clearer instructions, stronger revision habits, and reusable style constraints that make AI-assisted drafts feel edited by a human.

## Why This Exists

AI writing often fails in predictable ways:

| Problem | What this project adds |
| --- | --- |
| Generic "AI voice" | Concrete revision checks for rhythm, specificity, and empty phrasing |
| One style fits every genre | Separate Markdown `SKILLS` for different writing forms |
| Long text loses continuity | A compact ledger for facts, plot, promises, and voice anchors |
| Prompts become messy | A CLI that compiles style, context, and task into one clean instruction pack |
| Advice stays abstract | Rules are written as observable editing actions |

## Built-In Style Skills

| Skill | Use it for | Main focus |
| --- | --- | --- |
| `fiction` | literary or commercial fiction | point of view, scene pressure, character behavior |
| `argumentative` | essays and opinion pieces | thesis, evidence, counterargument, logical flow |
| `news-report` | news-style reports | factual order, attribution, neutral wording |
| `self-media` | social posts and creator essays | useful voice without empty hype |
| `academic-paper` | research writing | cautious claims, structure, terminology |
| `webnovel` | serialized genre fiction | hooks, payoffs, power rules, continuity |

## Deep Human-Trace Modules

These modules target deeper AI-writing artifacts, not only surface phrases.

| Module | What it repairs |
| --- | --- |
| `controlled-drift` | overly smooth logic, no associative movement, no unfinished thought |
| `narrative-bridges` | weak scene turns, generic transitions, paragraphs that do not cause each other |
| `relationship-state` | relationships that reset, dialogue without leverage, forgotten secrets or boundaries |
| `natural-measurement` | false precision: tiny exact measures and counted micro-actions in narrative prose |
| `cliche-phrase-audit` | stock phrases, generic body cues, empty emotion labels, and dead transitions |
| `formulaic-structure-audit` | triplets, symmetrical frames, and paragraphs that resolve too neatly |
| `prose-progress-audit` | polished paragraphs that do not add a new fact, action, proof, or pressure |
| `imperfect-prose` | prose that is too clean, too symmetrical, or too polished |
| `vocal-rhythm` | flat cadence and missing read-aloud breath points |
| `embodied-emotion` | emotion labels without body, action, contradiction, or perception |
| `cultural-anchors` | vacuum prose with no era, place, community, or material detail |
| `spatial-blocking` | character teleportation and confused front/back/left/right blocking |
| `occupancy-capacity` | over-occupied or mode-ambiguous seats, benches, beds, stools, aisles, and surfaces |
| `appearance-prop-continuity` | clothing, shoes, props, injuries, and daily-detail drift |
| `physical-continuity-audit` | final checks for position, movement gates, wardrobe, and props |
| `style-matrix` | the mistake of applying one generic "human voice" to every genre |
| `editor-loop` | one-shot drafting without a critical human-editor pass |
| `ai-trace-rubric` | vague feedback like "sounds AI" without diagnosis |

## Quick Start

```powershell
git clone https://github.com/whh110112/human-writing-skills.git
cd human-writing-skills

python -m humanwriting.cli list --kind style
python -m humanwriting.cli list --kind module
python -m humanwriting.cli build --style fiction --context examples/story-ledger.md --task "Write the next scene."
```

The `build` command prints an instruction pack that can be pasted into Codex, ChatGPT, Claude, local LLM tools, or another writing agent.

## Example Output Shape

```text
# Core Directive
# Continuity Protocol
# Selected Skill: fiction
# Project Context
# Task
# Output Contract
```

This format keeps the model focused on the current task while still carrying the previous facts, style decisions, and unresolved threads.

## Long-Form Continuity

For longer works, this project recommends a small ledger instead of relying only on a large context window.

The ledger tracks:

- fixed facts: names, dates, locations, relationships, rules, timeline
- active threads: unresolved conflicts, clues, promises, open arguments
- relationship state: who knows, wants, hides, owes, refuses, or holds leverage
- voice anchors: point of view, diction, pacing, formality, taboo phrases
- current state: where the previous passage ended and what must connect next
- beat bridge: previous residue, entry pressure, micro-turn, and exit hook
- change log: what became newly true in the latest output

See [examples/story-ledger.md](examples/story-ledger.md) for a fiction example.

## Chatbox

Yes, this project works in Chatbox because it outputs plain text prompt packs. For long writing sessions, use the continuity ledger as the source of truth and paste the compiled prompt pack into Chatbox's system prompt or first message.

- English guide: [docs/chatbox.md](docs/chatbox.md)
- Chinese guide: [docs/chatbox.zh-CN.md](docs/chatbox.zh-CN.md)
- Ledger template: [examples/chatbox-ledger-template.md](examples/chatbox-ledger-template.md)

## Physical Continuity

For scenes where space matters, such as cars, elevators, hospital rooms, dining tables, and bedrooms, use `--strict-continuity`. It automatically adds spatial blocking, appearance/prop continuity, and physical audit modules.

```powershell
python -m humanwriting.cli build `
  --style fiction `
  --strict-continuity `
  --review `
  --context examples/vehicle-scene-ledger.md `
  --task "Continue the car argument. Every seat change must have an on-page transition. Keep clothing and props consistent."
```

- Guide: [docs/physical-continuity.md](docs/physical-continuity.md)
- Vehicle ledger example: [examples/vehicle-scene-ledger.md](examples/vehicle-scene-ledger.md)
- Capacity ledger template: [examples/capacity-ledger-template.md](examples/capacity-ledger-template.md)
- Capacity conflict example: [examples/capacity-conflict-draft.zh-CN.md](examples/capacity-conflict-draft.zh-CN.md)
- Draft audit example: [examples/problem-car-scene-draft.md](examples/problem-car-scene-draft.md)

If the draft already exists, use `audit`:

```powershell
python -m humanwriting.cli audit `
  --draft examples/problem-car-scene-draft.md `
  --context examples/vehicle-scene-ledger.md
```

## Project Layout

```text
humanwriting/        Python package and CLI
skills/              reusable writing SKILLS in Markdown
examples/            sample continuity ledgers and article briefs
tests/               standard-library unit tests
```

## CLI Usage

### Number Sense

Use this to catch false precision such as unnecessary exact centimeters, seconds, or micro-counts in emotional and bodily action, while preserving necessary numbers in medicine, forensics, engineering, architecture, news, and technical writing.

```powershell
python -m humanwriting.cli audit `
  --draft examples/false-precision-draft.zh-CN.md `
  --numbers `
  --no-strict-continuity
```

- Guide: [docs/number-sense.md](docs/number-sense.md)
- Example: [examples/false-precision-draft.zh-CN.md](examples/false-precision-draft.zh-CN.md)

### Forum Complaint Research

The project converts recurring public complaints about AI writing into executable checks: stock phrasing, plastic prose, triplet structures, over-smooth transitions, static paragraphs, hollow emotion, cultural vacuum, and long-form drift.

- Research map: [docs/forum-complaint-research.md](docs/forum-complaint-research.md)

List styles:

```powershell
python -m humanwriting.cli list
```

Build a prompt pack:

```powershell
python -m humanwriting.cli build `
  --style webnovel `
  --module narrative-bridges `
  --module relationship-state `
  --module natural-measurement `
  --module embodied-emotion `
  --module vocal-rhythm `
  --strict-continuity `
  --review `
  --context examples/story-ledger.md `
  --task "Continue chapter 3. Keep the confrontation unresolved but reveal one new clue."
```

The `--review` flag adds these modules automatically:

- `editor-loop`: draft, diagnose, locally rewrite, then finalize
- `ai-trace-rubric`: score cognitive smoothness, generic diction, emotional flatness, rhythm monotony, context drift, weak beat bridges, relationship resets, false precision, cultural vacuum, over-clean prose, and closure addiction
- `cliche-phrase-audit`: check stock phrases, generic body cues, empty emotion labels, and dead transitions
- `formulaic-structure-audit`: check triplets, symmetrical frames, and paragraphs that close too neatly
- `prose-progress-audit`: check whether each paragraph advances facts, relationships, evidence, action, or pressure

The `--strict-continuity` flag adds:

- `spatial-blocking`: position and movement checks
- `occupancy-capacity`: physical resource mode, capacity, occupancy, and transformation checks
- `appearance-prop-continuity`: clothing, shoes, props, and body-state checks
- `physical-continuity-audit`: final physical-state contradiction pass

Run tests:

```powershell
python -m unittest discover -s tests -v
```

## Writing Philosophy

Good AI-assisted prose should be:

- situated: it knows who is speaking, what changed, and why this passage exists
- specific: it uses details that belong to this topic, not any topic
- continuous: it respects previous facts, costs, injuries, claims, and promises
- shaped: it understands the genre before choosing structure and diction
- revised: it removes filler, canned transitions, and decorative certainty

## Editorial Guardrails

This project avoids claiming that any tool can perfectly hide authorship or beat detectors. It focuses on craft: voice, context, genre, revision, and continuity.

When studying published work, use short analysis, public-domain sources, licensed material, or your own examples. Do not copy protected passages into skills.

## Contributing

Contributions are welcome. Useful additions include:

- new Markdown skills
- Chinese and multilingual style packs
- model-specific adapters
- stronger continuity ledger examples
- tests for prompt compilation and context preservation

Please keep each skill practical. A good rule should tell the model what to do, what to avoid, and how to check the result.

## License

MIT. See [LICENSE](LICENSE).
