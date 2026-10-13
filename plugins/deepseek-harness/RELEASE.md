DSH Writing Plugin 0.2.0 bundles Human Writing core 0.16.0 and all writing modules.

- Generation-time guidance for novels, papers, reports, essays, and rewriting.
- Local prompt compilation, voice preservation, factual-source grounding, lint,
  protected-content and semantic-fidelity triage, and bounded long-form review.
- Isolated bundled Python startup; no extra pip installation of the core.
- Official Cordis/MCP integration tests and Linux/Windows CI.

Install:

```sh
dsh plugin --profile web add https://github.com/whh110112/human-writing-skills/releases/download/dsh-v0.2.0/dsh-advanced-human-writing.tgz
```

Use `desktop` for a desktop profile. Requires Python 3.9+ and Node ^22.19.0 or >=24.
Tested against official DSH 0.2.1-alpha.2 packages. Writing remains performed by
the user's DSH model; no authorship-detector or quantified quality claim is made.
