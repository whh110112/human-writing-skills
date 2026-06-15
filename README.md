# Human Writing Skills

Human Writing Skills is an open-source skill pack and small CLI for making AI-assisted writing less formulaic, more context-aware, and easier to steer across genres.

The project focuses on three practical problems:

- reducing repetitive, generic, "AI-shaped" prose habits
- switching writing style through reusable `SKILLS`
- keeping long-form writing aligned with previous plot, facts, tone, and constraints

It does not try to hide authorship or encourage deception. The goal is better editing, stronger voice control, and more faithful continuity.

## Features

- Markdown-based writing skills for fiction, argumentative essays, news reports, self-media posts, academic papers, and web novels
- a continuity ledger for characters, facts, plot promises, unresolved threads, and style decisions
- a prompt compiler that combines the selected style skill with project context
- a lightweight Python CLI with no required third-party dependencies
- examples that can be copied into Codex, ChatGPT, Claude, local LLM tools, or other writing agents

## Quick Start

```powershell
cd human-writing-skills
python -m humanwriting.cli list
python -m humanwriting.cli build --style fiction --context examples/story-ledger.md --task "Write the next scene."
```

The `build` command prints an instruction pack you can give to an AI writing assistant.

## Available Skills

- `fiction`: character-driven literary and commercial fiction
- `argumentative`: essays with clear claims, evidence, and counterargument
- `news-report`: concise news writing with source discipline
- `self-media`: natural social/media-account posts without empty hype
- `academic-paper`: formal research prose with cautious claims
- `webnovel`: serialized genre fiction with continuity and hooks

## Project Layout

```text
humanwriting/        Python package and CLI
skills/              reusable writing SKILLS in Markdown
examples/            sample continuity ledgers and tasks
tests/               focused unit tests
```

## Design Principles

1. Voice before decoration.
   Good prose is shaped by intention, audience, rhythm, and specificity.

2. Context before output.
   Long writing needs a ledger of facts, promises, relationships, and tone decisions.

3. Revision before disguise.
   The system asks the model to revise for concrete human qualities: varied sentence movement, grounded detail, clean transitions, and less canned phrasing.

4. Genre as constraints.
   A style skill is not a costume. It is a set of choices about evidence, pacing, diction, structure, and reader expectation.

## Example

```powershell
python -m humanwriting.cli build `
  --style webnovel `
  --context examples/story-ledger.md `
  --task "Continue chapter 3. Keep the confrontation unresolved but reveal one new clue."
```

## Contributing

Contributions are welcome:

- new writing skills
- better continuity ledger formats
- examples in more languages
- model-specific adapters
- tests for prompt compilation and context preservation

Please keep skills concrete. Avoid generic rules like "write naturally" unless they are paired with observable editing checks.

## License

MIT
