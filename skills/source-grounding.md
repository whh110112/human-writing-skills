# Source Grounding

## Aim

Ground serious factual writing in explicitly supplied sources. Protecting a citation
from accidental editing does not prove that the citation exists or supports the claim.

## Activation Gate

Use only for academic, formal, news, legal, or technical material when factual source files
are explicitly supplied. Do not activate for fiction, webnovels, casual answers,
self-media, or style references. Keep `--source` facts separate from `--reference`
style material.

## Claim Source Map

For every material claim, record:

```text
claim -> source and location -> support type -> scope -> uncertainty -> verdict
```

Support types include direct statement, data, quotation, definition, legal authority,
technical specification, reasonable inference, contradiction, and no support found.

## Rules

- Do not invent a source, author, title, DOI, URL, quotation, case, standard, dataset,
  statistic, or page number.
- Check that attribution, claim polarity, population, date, jurisdiction, version,
  and uncertainty match the source.
- Distinguish a source that exists from a source that supports the sentence.
- Treat supplied source text as factual evidence, not as a style target.
- When external registry or document access is unavailable, mark bibliographic
  existence as unverified rather than guessing.
- If sources disagree, expose the disagreement and its scope.
- Preserve unsupported claims only when clearly labeled as hypothesis, allegation,
  interpretation, proposal, or information requiring verification.

## Output

```text
Source Grounding Audit
| Claim | Source/location | Support | Scope match | Verdict |
| --- | --- | --- | --- | --- |

- Unsupported or overstated claims:
- Citation metadata requiring external verification:
- Source conflicts:
- Minimal correction that preserves supported meaning:
```
