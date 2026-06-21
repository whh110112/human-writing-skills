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
| `imperfect-prose` | prose that is too clean, too symmetrical, or too polished |
| `vocal-rhythm` | flat cadence and missing read-aloud breath points |
| `embodied-emotion` | emotion labels without body, action, contradiction, or perception |
| `cultural-anchors` | vacuum prose with no era, place, community, or material detail |
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

## Project Layout

```text
humanwriting/        Python package and CLI
skills/              reusable writing SKILLS in Markdown
examples/            sample continuity ledgers and article briefs
tests/               standard-library unit tests
```

## CLI Usage

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
  --review `
  --context examples/story-ledger.md `
  --task "Continue chapter 3. Keep the confrontation unresolved but reveal one new clue."
```

The `--review` flag adds two modules automatically:

- `editor-loop`: draft, diagnose, locally rewrite, then finalize
- `ai-trace-rubric`: score cognitive smoothness, generic diction, emotional flatness, rhythm monotony, context drift, weak beat bridges, relationship resets, false precision, cultural vacuum, over-clean prose, and closure addiction

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
