# Advanced Human Writing for DeepSeek Harness

This DeepSeek Harness bundle mounts the `human-writing-mcp` tools from the
parent repository. It coordinates bounded long-form reviews locally: create a
plan, let separate agents claim focused work, require complete coverage
receipts, and unlock the final reconciliation only after verification passes.

## Prerequisites

Install the Python package in the environment selected by `PYTHON` or `python`:

```powershell
pip install human-writing-skills
```

For development from this repository:

```powershell
pip install -e .
```

## Install

After publishing this folder to npm, add it to a DeepSeek Harness profile:

```powershell
dsh plugin --profile web add dsh-advanced-human-writing
```

Restart the affected DSH profile. The bundle uses the workspace as its allowed
file root. Set `PYTHON` before launching DSH when the desired interpreter is
not named `python`.

The mounted tools are `plan_long_form_audit`, `list_audit_tasks`,
`claim_audit_task`, `submit_audit_report`, `verify_audit_coverage`,
`get_reconciliation_task`, and `read_project_context`.

This package does not send drafts to a third party and does not call a model by
itself. The active DSH agent performs each assigned review and must submit its
own report.
