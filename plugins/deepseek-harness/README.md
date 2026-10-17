# Human Writing for DeepSeek Harness

A DSH/Cordis plugin for novels, papers, reports, essays, and supplied-draft cleanup.
It contributes a compact writing protocol before generation and mounts local tools
for genre-aware prompt compilation, lint, factual fidelity, voice preservation,
and bounded long-form review. The existing DSH agent writes the prose; this plugin
does not make a separate model call or promise authorship-detector scores.

## Install

Requires Python 3.9+ on PATH and a DSH profile with tools and systemPrompt services.
No pip installation of human-writing-skills is needed: the release bundles its Python
core and Markdown modules. Use Node ^22.19.0 or >=24.0.0 as required by current DSH.
Integration-tested with official DSH 0.2.1-alpha.2 packages. Peer ranges also admit
0.2.0-rc.2 and the 0.2.1 alpha line; those other versions have not been tested here.

```powershell
dsh plugin --profile web add https://github.com/whh110112/human-writing-skills/releases/download/dsh-v0.2.1/dsh-advanced-human-writing.tgz
```

For the desktop profile, replace `web` with `desktop`. Restart the affected profile.
If Python is not named `python`, set `PYTHON` to its executable path before starting DSH.
Alternatively, install the complete repository root at a pinned tag:

```powershell
dsh plugin --profile web add github:whh110112/human-writing-skills#dsh-v0.2.1
```

The npm package manifest lives at the repository root. The adapter subfolder is
private and is not a standalone npm package. No npm publication is claimed.

## Use In DSH

- Novel: “Use Human Writing to continue the scene in Chinese. Preserve the supplied
  character ledger and let both speakers respond; avoid a reflective tail.”
- Paper: “Write the results section from these observations. Preserve uncertainty;
  do not invent citations, statistics, or significance tests.”
- Report: “Write the weekly report with current status, blockers, owners, and next steps.
  Keep planned work separate from completed work.”
- Rewrite: “Polish this draft while preserving my voice, meaning, and useful ambiguity.”
- Advice: “Diagnose this article without rewriting it.”

The model receives the plugin's conditional guidance only for authored writing,
rewriting, or review. It is instructed to call `mcp__human-writing__compile_generation_prompt`
before substantive generation, apply the returned genre protocol, and use lint and
fidelity tools before delivery where relevant. These remain model-followed instructions,
not a guarantee that a model will follow every rule. Deep audits load only on demand.

Use workspace-relative `source_paths` for factual evidence and `reference_paths`
for voice samples; both are restricted to the configured root. They are distinct.
The compiler will not borrow facts from a voice sample. See runnable input examples
in [examples](examples) and a [keyless integration demo](DEMO.md).

## Configuration

The supplied patch mounts the plugin as `advanced-human-writing-mcp`.

| Field | Default | Purpose |
| --- | --- | --- |
| root | DSH launch working directory | Allowed writing workspace |
| pythonCommand | PYTHON or python | Python executable, not a shell command |
| serverName | human-writing | MCP namespace; tool and guidance names follow it |
| generationGuidance | true | Set false to keep tools without the prompt section |
| toolCallTimeoutMs | 60000 | Individual tool timeout |

Config `root` explicitly when DSH is launched outside the writing project. Python
starts in isolated mode and loads the bundled core before workspace modules.

## Permissions And Distribution

The plugin starts a local Python stdio process. The local core reads supplied text
and workspace files, and writes review packages only through invoked planning/report
tools. It does not install Python packages, open a network listener, upload drafts,
or publish generated writing. DSH's configured model receives the text used in its
normal conversation and calls; its existing provider/privacy settings still apply.
External publication of a manuscript requires the user's instruction to DSH.

Category: Skills / Tools & Capabilities. License: MIT. This is a community plugin,
not an official DeepSeek product. Market submission and maintainer acceptance are
separate from publishing an installable release.

## Development

From the repository root:

```powershell
pnpm install --frozen-lockfile
pnpm test
python -m unittest discover -s tests -q
pnpm pack --pack-destination dist
```

Tests negotiate with the real bundled server, compile fiction/paper/report prompts,
verify facts, reject path escapes, and mount/call/unload through official Cordis and
MCP packages without any model/API key. They verify integration, not literary quality.
