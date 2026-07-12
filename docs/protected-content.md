# Protected Content Verification

## Conditional Activation

Automatic protection is deliberately narrow:

- `academic-paper` and `news-report` generation enable it by document type.
- Legal and technical drafts require multiple matching document cues.
- Fiction, webnovels, self-media, casual Q&A, playful output, and roleplay do not
  auto-enable it. A number or proper noun by itself is never sufficient.
- `--protect-content` or `--protect-term` always overrides automatic selection.

For untyped audits, use `--document-type legal`, `technical`, `academic-paper`, or
`news-report` when the automatic evidence is too sparse. Use a narrative document
type to suppress a false positive. In a pipeline, automatic protection is loaded in
one final selected stage only to avoid repeating the same token-heavy manifest.

The skill also locks claim polarity, findings, limitations, attribution, and
conclusion direction. The CLI can mechanically recognize some acronyms, standards,
product identifiers, and formal `《titles》`, but it is not a complete named-entity
recognizer. Pass important names with `--protect-term`.

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
