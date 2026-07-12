# Protected Content Verification

Rewriting can silently alter a percentage, citation, equation, URL, code fragment,
quotation, or required term. Protection has two steps:

1. Add `--protect-content` or `--protect-term` to an audit so the model receives a
   manifest and must flag questionable facts instead of changing them.
2. Run `verify` after revision for a deterministic source-to-candidate comparison.

```powershell
human-writing-skills audit --draft original.md --protect-content --protect-term "Project Atlas"
human-writing-skills verify --source original.md --candidate revised.md --protect-term "Project Atlas"
```

Exit code `0` means all source items remain present; exit code `1` means at least
one is missing or changed. Added protected-looking values are reported separately.
Verification checks textual preservation, not whether the source fact was correct.
