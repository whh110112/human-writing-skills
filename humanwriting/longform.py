from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .compiler import read_optional
from .reference import build_reference_pack, sample_reference
from .skills import list_style_skills, load_skill
from .statistics import StyleStatistics, analyze_style_statistics, format_style_statistics


DEFAULT_CHUNK_SIZE = 8000
DEFAULT_OVERLAP_SIZE = 600
DEFAULT_CONTEXT_BUDGET = 6000
DEFAULT_BASELINE_BUDGET = 4000
MIN_CHUNK_SIZE = 2000
NARRATIVE_STYLES = {"fiction", "webnovel"}
SERIOUS_STYLES = {"academic-paper", "formal-document", "news-report"}
DIALOGUE_PATTERN = re.compile(r"[\"“‘「『].{1,240}?[\"”’」』]", re.DOTALL)
SPLIT_PATTERNS = (
    re.compile(r"\n\s*\n"),
    re.compile(r"(?<=[。！？!?])(?:[\"”’」』】）)])?"),
    re.compile(r"\n"),
)


@dataclass(frozen=True)
class TextChunk:
    index: int
    start: int
    end: int
    lead_start: int
    lead_in: str
    body: str


@dataclass(frozen=True)
class ChunkDiagnostic:
    index: int
    start: int
    end: int
    character_count: int
    average_sentence_length: float
    sentence_length_cv: float
    paragraph_length_cv: float | None
    mattr: float | None
    transition_density_per_1000: float
    candidate_drift: tuple[str, ...]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["candidate_drift"] = list(self.candidate_drift)
        return data


def _preferred_split(text: str, start: int, target: int) -> int:
    if target >= len(text):
        return len(text)
    floor = start + max(1, (target - start) // 2)
    search_start = max(floor, target - 1600)
    for pattern in SPLIT_PATTERNS:
        candidates = [match.end() for match in pattern.finditer(text, search_start, target)]
        if candidates:
            return candidates[-1]
    return target


def split_long_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP_SIZE,
) -> list[TextChunk]:
    if chunk_size < MIN_CHUNK_SIZE:
        raise ValueError(f"Chunk size must be at least {MIN_CHUNK_SIZE} characters.")
    if overlap < 0:
        raise ValueError("Overlap must be zero or greater.")
    if overlap >= chunk_size // 2:
        raise ValueError("Overlap must be smaller than half the chunk size.")
    if not text:
        raise ValueError("Long-form audit requires a non-empty draft.")

    chunks: list[TextChunk] = []
    start = 0
    while start < len(text):
        end = _preferred_split(text, start, min(len(text), start + chunk_size))
        if end <= start:
            end = min(len(text), start + chunk_size)
        lead_start = max(0, start - overlap)
        chunks.append(
            TextChunk(
                index=len(chunks) + 1,
                start=start,
                end=end,
                lead_start=lead_start,
                lead_in=text[lead_start:start],
                body=text[start:end],
            )
        )
        start = end
    return chunks


def _sample_paths(paths: list[str] | None, budget: int) -> tuple[str, tuple[str, ...]]:
    unique_paths = [Path(path) for path in dict.fromkeys(paths or [])]
    if not unique_paths:
        return "", ()
    per_source, remainder = divmod(budget, len(unique_paths))
    samples: list[str] = []
    names: list[str] = []
    for index, path in enumerate(unique_paths):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"Reference file is empty: {path}")
        source_budget = per_source + (1 if index < remainder else 0)
        samples.append(sample_reference(text, source_budget))
        names.append(path.name)
    return "\n\n".join(samples), tuple(names)


def _change_ratio(value: float, baseline: float) -> float | None:
    if baseline == 0:
        return None
    return value / baseline


def _diagnose_chunk(
    chunk: TextChunk,
    baseline: StyleStatistics,
    style: str,
) -> tuple[StyleStatistics, ChunkDiagnostic]:
    report = analyze_style_statistics(chunk.body, style=style)
    flags: list[str] = []
    sentence_ratio = _change_ratio(report.average_sentence_length, baseline.average_sentence_length)
    if sentence_ratio is not None and (sentence_ratio < 0.65 or sentence_ratio > 1.55):
        flags.append("average sentence length differs materially from the baseline")
    if abs(report.sentence_length_cv - baseline.sentence_length_cv) > 0.25:
        flags.append("sentence-length variation differs materially from the baseline")
    if report.paragraph_length_cv is not None and baseline.paragraph_length_cv is not None:
        if abs(report.paragraph_length_cv - baseline.paragraph_length_cv) > 0.3:
            flags.append("paragraph-weight variation differs materially from the baseline")
    if report.mattr is not None and baseline.mattr is not None:
        if abs(report.mattr - baseline.mattr) > 0.15:
            flags.append("lexical diversity differs materially from the baseline")
    if abs(
        report.transition_density_per_1000 - baseline.transition_density_per_1000
    ) > 12:
        flags.append("explicit-transition density differs materially from the baseline")
    diagnostic = ChunkDiagnostic(
        index=chunk.index,
        start=chunk.start,
        end=chunk.end,
        character_count=len(chunk.body),
        average_sentence_length=report.average_sentence_length,
        sentence_length_cv=report.sentence_length_cv,
        paragraph_length_cv=report.paragraph_length_cv,
        mattr=report.mattr,
        transition_density_per_1000=report.transition_density_per_1000,
        candidate_drift=tuple(flags),
    )
    return report, diagnostic


def _module_block(name: str) -> str:
    return f"# Audit Module: {name}\n\n{load_skill(name).content}"


def _base_prompt_sections(style: str) -> list[str]:
    style_skill = load_skill(style)
    return [
        f"# Selected Style: {style}",
        style_skill.content,
        _module_block("long-form-style-consistency"),
    ]


def _format_diagnostics(
    baseline: StyleStatistics,
    diagnostics: list[ChunkDiagnostic],
) -> str:
    rows = [
        "# Cross-Chunk Style Diagnostics",
        "",
        "These distributional differences are review leads, not proof of a defect or authorship.",
        "Topic, scene function, quoted material, and deliberate character development may explain them.",
        "",
        "## Baseline",
        "",
        format_style_statistics(baseline, "markdown").strip(),
        "",
        "## Chunks",
        "",
        "| Chunk | Characters | Avg sentence | Sentence CV | Paragraph CV | MATTR | Transitions/1000 | Candidate drift |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in diagnostics:
        paragraph_cv = "n/a" if item.paragraph_length_cv is None else str(item.paragraph_length_cv)
        mattr = "n/a" if item.mattr is None else str(item.mattr)
        flags = "; ".join(item.candidate_drift) or "none from deterministic thresholds"
        rows.append(
            f"| {item.index} | {item.character_count} | {item.average_sentence_length} | "
            f"{item.sentence_length_cv} | {paragraph_cv} | {mattr} | "
            f"{item.transition_density_per_1000} | {flags} |"
        )
    return "\n".join(rows) + "\n"


def write_long_form_audit(
    draft_path: str,
    output_dir: str,
    style: str,
    context_path: str | None = None,
    reference_paths: list[str] | None = None,
    reference_style: str | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP_SIZE,
    baseline_chunk: int = 1,
    context_budget: int = DEFAULT_CONTEXT_BUDGET,
    baseline_budget: int = DEFAULT_BASELINE_BUDGET,
) -> tuple[Path, list[TextChunk]]:
    if style not in list_style_skills():
        raise ValueError(f"Unknown style '{style}'.")
    if context_budget < 1000:
        raise ValueError("Context budget must be at least 1000 characters.")
    if baseline_budget < 1000:
        raise ValueError("Baseline budget must be at least 1000 characters.")

    draft = Path(draft_path).read_text(encoding="utf-8")
    if not draft.strip():
        raise ValueError("Long-form audit requires a non-empty --draft file.")
    chunks = split_long_text(draft, chunk_size=chunk_size, overlap=overlap)
    if not 1 <= baseline_chunk <= len(chunks):
        raise ValueError(f"Baseline chunk must be between 1 and {len(chunks)}.")

    context = read_optional(context_path)
    context_sample = sample_reference(context, context_budget) if context else ""
    reference_sample, reference_names = _sample_paths(reference_paths, baseline_budget)
    reference_pack = build_reference_pack(
        reference_paths,
        reference_style,
        budget=baseline_budget,
    )
    selected_baseline = chunks[baseline_chunk - 1]
    baseline_text = reference_sample or sample_reference(selected_baseline.body, baseline_budget)
    baseline_source = (
        f"explicit reference files: {', '.join(reference_names)}"
        if reference_names
        else f"manuscript chunk {baseline_chunk} (candidate baseline; confirm before repair)"
    )
    if reference_style and not reference_names:
        baseline_source += " plus explicit style direction"
    baseline_stats = analyze_style_statistics(baseline_text, style=style)

    reports: list[StyleStatistics] = []
    diagnostics: list[ChunkDiagnostic] = []
    for chunk in chunks:
        report, diagnostic = _diagnose_chunk(chunk, baseline_stats, style)
        reports.append(report)
        diagnostics.append(diagnostic)

    output = Path(output_dir)
    if output.exists() and any(output.iterdir()):
        raise ValueError(
            "Long-form audit output directory must be empty to avoid stale chunk prompts."
        )
    output.mkdir(parents=True, exist_ok=True)
    diagnostic_text = _format_diagnostics(baseline_stats, diagnostics)
    (output / "00-style-drift.md").write_text(diagnostic_text, encoding="utf-8")
    diagnostic_json = {
        "disclaimer": "Distributional editing diagnostics, not authorship evidence.",
        "style": style,
        "baseline_source": baseline_source,
        "baseline": baseline_stats.to_dict(),
        "chunks": [item.to_dict() for item in diagnostics],
    }
    (output / "00-style-drift.json").write_text(
        json.dumps(diagnostic_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    shared_sections = _base_prompt_sections(style)
    if style in NARRATIVE_STYLES and context:
        shared_sections.append(_module_block("character-consistency-audit"))
    if style in SERIOUS_STYLES:
        shared_sections.append(_module_block("protected-content"))
    baseline_evidence = reference_pack.block if reference_pack.active else (
        "# Candidate Baseline Excerpt\n\n" + baseline_text
    )
    if context_sample:
        context_block = (
            "# Outline / Continuity Authority\n\n"
            "Treat this as canonical for facts, character settings, terminology, and claim boundaries as applicable. "
            "A later explicit change gate may update it.\n\n"
            + context_sample
        )
    else:
        context_block = (
            "# Outline / Continuity Authority\n\n"
            "No outline or continuity ledger was supplied. Treat inferred character traits as provisional, not canon."
        )

    baseline_prompt = "\n\n".join(
        [
            "# Long-Form Baseline Extraction",
            "Build a compact, evidence-backed style contract for later chunk audits. "
            "Do not rewrite the manuscript in this pass. Separate stable voice from topic- or scene-specific variation.",
            *shared_sections,
            context_block,
            baseline_evidence,
            "# Baseline Statistics\n\n" + format_style_statistics(baseline_stats).strip(),
            "# Required Output\n\n"
            "Return: stable style anchors; permitted range; character cards supported by the outline; "
            "speaker voice anchors; deliberate evolution gates; serious-document terminology and claim-scope rules; "
            "and uncertain items that must not be treated as canon. Keep the result compact enough to reuse in every chunk pass.",
        ]
    ) + "\n"
    (output / "00-baseline-prompt.md").write_text(baseline_prompt, encoding="utf-8")

    for chunk, report in zip(chunks, reports):
        chunk_sections = list(shared_sections)
        if style in NARRATIVE_STYLES and DIALOGUE_PATTERN.search(chunk.body):
            chunk_sections.append(_module_block("dialogue-voice-audit"))
        lead_in = chunk.lead_in or "[No prior lead-in: this is the first chunk.]"
        prompt = "\n\n".join(
            [
                f"# Long-Form Chunk Audit {chunk.index}/{len(chunks)}",
                "Audit only the numbered body below. The lead-in is read-only continuity context: "
                "do not report or rewrite a problem located only in that lead-in. Compare against the approved baseline and outline, "
                "but allow evidence-backed shifts caused by viewpoint, section function, time, pressure, or character development.",
                *chunk_sections,
                context_block,
                baseline_evidence,
                "# Baseline Statistics\n\n" + format_style_statistics(baseline_stats).strip(),
                "# Current Chunk Statistics\n\n" + format_style_statistics(report).strip(),
                f"# Read-Only Lead-In ({chunk.lead_start}:{chunk.start})\n\n{lead_in}",
                f"# Audited Body ({chunk.start}:{chunk.end})\n\n{chunk.body}",
                "# Required Output\n\n"
                "Locate evidence by body character offset or a short quotation. Separate confirmed drift, plausible intentional variation, "
                "and insufficient evidence. For fiction, compare each character with outline-backed goals, knowledge, relationships, "
                "behavioral limits, and speaker voice; require an on-page change gate before accepting a contradiction. For serious text, "
                "preserve facts, figures, quotations, terminology, attribution, uncertainty, and conclusion scope. Recommend the smallest local repair, "
                "then emit a compact state-and-voice delta for the next chunk. Do not normalize every sentence or character into one average voice.",
            ]
        ) + "\n"
        (output / f"{chunk.index:04d}-chunk-audit.md").write_text(prompt, encoding="utf-8")

    reconcile_prompt = "\n\n".join(
        [
            "# Long-Form Cross-Chunk Reconciliation",
            "Use the approved baseline report, `00-style-drift.md`, and all completed chunk-audit reports. "
            "Do not infer a global defect from one statistical outlier. Require quoted or located evidence from at least two relevant blocks, "
            "unless one block directly contradicts the canonical outline.",
            _module_block("long-form-style-consistency"),
            context_block,
            diagnostic_text.strip(),
            "# Required Output\n\n"
            "Produce: a ranked cross-chunk drift table; recurring narrator-style changes; per-character dialogue and behavior conflicts; "
            "valid development or section-function changes; a minimal repair sequence; and ledger updates. Resolve facts and character canon before style, "
            "then voice, rhythm, and surface wording. Re-audit neighboring blocks after structural repairs.",
        ]
    ) + "\n"
    (output / "9999-reconcile-prompt.md").write_text(reconcile_prompt, encoding="utf-8")

    manifest = {
        "draft": str(Path(draft_path)),
        "style": style,
        "chunk_size": chunk_size,
        "lead_in_overlap": overlap,
        "baseline_source": baseline_source,
        "context_supplied": bool(context),
        "chunks": [
            {
                "index": chunk.index,
                "start": chunk.start,
                "end": chunk.end,
                "lead_start": chunk.lead_start,
                "body_characters": len(chunk.body),
                "lead_in_characters": len(chunk.lead_in),
                "prompt": f"{chunk.index:04d}-chunk-audit.md",
            }
            for chunk in chunks
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    guide = "\n".join(
        [
            "# Long-Form Chunk Audit Package",
            "",
            f"- Draft style: `{style}`",
            f"- Unique audit chunks: `{len(chunks)}`",
            f"- Baseline source: {baseline_source}",
            f"- Outline / continuity context: `{'supplied' if context else 'not supplied'}`",
            "",
            "1. Run `00-baseline-prompt.md` first and approve or correct its compact style/character contract.",
            "2. Run each numbered chunk prompt independently. Supply the approved contract when your model or client does not retain files.",
            "3. Save each report. The lead-in is context only, so findings from adjacent blocks are not double-counted.",
            "4. Run `9999-reconcile-prompt.md` with the completed reports and approved baseline.",
            "5. Apply repairs from canon and meaning to character state, voice, rhythm, then surface wording; re-audit affected neighbors.",
            "",
            "`00-style-drift.md` is a deterministic triage map. Its outliers are review leads, not automatic defects.",
            "For fiction, an outline or continuity ledger is required for authoritative character-setting checks.",
            "For reports, use the outline/context file for terminology, claim scope, section purpose, and source boundaries.",
            "",
        ]
    )
    (output / "README.md").write_text(guide, encoding="utf-8")
    return output, chunks
