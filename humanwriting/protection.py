from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProtectedItem:
    kind: str
    value: str
    count: int


@dataclass(frozen=True)
class ProtectionDifference:
    kind: str
    value: str
    expected_count: int
    actual_count: int


@dataclass(frozen=True)
class ProtectionReport:
    ok: bool
    source_items: tuple[ProtectedItem, ...]
    missing_or_changed: tuple[ProtectionDifference, ...]
    added: tuple[ProtectionDifference, ...]

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "source_items": [asdict(item) for item in self.source_items],
            "missing_or_changed": [asdict(item) for item in self.missing_or_changed],
            "added": [asdict(item) for item in self.added],
        }


PROTECTED_PATTERNS = [
    ("fenced-code", re.compile(r"```.*?```", re.DOTALL)),
    ("source-quote", re.compile(r"(?m)^\s*>\s+.+$")),
    ("inline-code", re.compile(r"`[^`\n]+`")),
    ("url", re.compile(r"https?://[^\s)>]+")),
    ("citation", re.compile(r"\\cite\{[^}]+\}|\[[0-9][0-9,;\s\-–—]*\]")),
    ("equation", re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.DOTALL)),
]
NUMBER_PATTERN = re.compile(
    r"(?<![\w.])[+-]?\d+(?:\.\d+)?(?:\s*(?:%|毫米|厘米|米|公里|秒|分钟|小时|"
    r"元|美元|岁|mg|g|kg|mm|cm|km|ms|s|min|h))?",
    re.IGNORECASE,
)


def _overlaps(span: tuple[int, int], occupied: list[tuple[int, int]]) -> bool:
    return any(span[0] < end and start < span[1] for start, end in occupied)


def extract_protected_items(text: str, terms: list[str] | None = None) -> list[ProtectedItem]:
    values: list[tuple[str, str]] = []
    occupied: list[tuple[int, int]] = []
    for kind, pattern in PROTECTED_PATTERNS:
        for match in pattern.finditer(text):
            if _overlaps(match.span(), occupied):
                continue
            values.append((kind, match.group(0)))
            occupied.append(match.span())
    for match in NUMBER_PATTERN.finditer(text):
        if not _overlaps(match.span(), occupied):
            values.append(("number", match.group(0)))
    for term in dict.fromkeys(terms or []):
        if term:
            values.extend(("explicit-term", term) for _ in range(text.count(term)))
    counts = Counter(values)
    return [
        ProtectedItem(kind, value, count)
        for (kind, value), count in sorted(counts.items(), key=lambda item: (item[0][0], item[0][1]))
    ]


def compare_protected_content(
    source: str,
    candidate: str,
    terms: list[str] | None = None,
) -> ProtectionReport:
    source_items = extract_protected_items(source, terms)
    candidate_items = extract_protected_items(candidate, terms)
    source_counts = {(item.kind, item.value): item.count for item in source_items}
    candidate_counts = {(item.kind, item.value): item.count for item in candidate_items}
    missing = []
    added = []
    for key, expected in source_counts.items():
        actual = candidate_counts.get(key, 0)
        if actual < expected:
            missing.append(ProtectionDifference(key[0], key[1], expected, actual))
    for key, actual in candidate_counts.items():
        expected = source_counts.get(key, 0)
        if actual > expected:
            added.append(ProtectionDifference(key[0], key[1], expected, actual))
    return ProtectionReport(
        ok=not missing and not added,
        source_items=tuple(source_items),
        missing_or_changed=tuple(missing),
        added=tuple(added),
    )


def compare_protected_files(
    source_path: str,
    candidate_path: str,
    terms: list[str] | None = None,
) -> ProtectionReport:
    source = Path(source_path).read_text(encoding="utf-8")
    candidate = Path(candidate_path).read_text(encoding="utf-8")
    return compare_protected_content(source, candidate, terms)


def build_protection_manifest(text: str, terms: list[str] | None = None) -> str:
    items = extract_protected_items(text, terms)
    present_explicit_terms = {
        item.value for item in items if item.kind == "explicit-term"
    }
    items.extend(
        ProtectedItem("explicit-term", term, max(1, text.count(term)))
        for term in dict.fromkeys(terms or [])
        if term and term not in present_explicit_terms
    )
    lines = [
        "# Protected Content Manifest",
        "",
        "Preserve every listed item and occurrence count exactly. Flag suspected errors instead of changing them.",
        "",
        "| Kind | Count | Value |",
        "| --- | --- | --- |",
    ]
    for item in items:
        value = item.value.replace("\n", " ").replace("|", "\\|")
        if len(value) > 160:
            value = value[:157] + "..."
        lines.append(f"| {item.kind} | {item.count} | `{value}` |")
    if not items:
        lines.append("| none detected | 0 | Add explicit `--protect-term` values if needed. |")
    return "\n".join(lines)


def format_protection_report(report: ProtectionReport, output_format: str = "markdown") -> str:
    if output_format == "json":
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"
    lines = [
        "# Protected Content Verification",
        "",
        f"- Status: {'PASS' if report.ok else 'FAIL'}",
        f"- Source items: {len(report.source_items)}",
        f"- Missing or changed: {len(report.missing_or_changed)}",
        f"- Added protected-looking items: {len(report.added)}",
        "",
        "## Missing or changed",
        "",
        "| Kind | Expected | Actual | Value |",
        "| --- | --- | --- | --- |",
    ]
    for item in report.missing_or_changed:
        value = item.value.replace("\n", " ").replace("|", "\\|")
        lines.append(f"| {item.kind} | {item.expected_count} | {item.actual_count} | `{value}` |")
    if not report.missing_or_changed:
        lines.append("| none | - | - | - |")
    lines.extend(
        [
            "",
            "## Added protected-looking items",
            "",
            "| Kind | Source | Candidate | Value |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in report.added:
        value = item.value.replace("\n", " ").replace("|", "\\|")
        lines.append(f"| {item.kind} | {item.expected_count} | {item.actual_count} | `{value}` |")
    if not report.added:
        lines.append("| none | - | - | - |")
    return "\n".join(lines) + "\n"
