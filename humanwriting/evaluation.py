from __future__ import annotations

import json
from pathlib import Path

from .fidelity import compare_fidelity
from .protection import detect_serious_document


VALID_KINDS = {"serious-detection", "fidelity"}
VALID_REVIEWS = {"seed", "native-reviewed"}


def evaluate_cases(path: str) -> dict:
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("Benchmark file must contain a JSON array.")
    rows = []
    ids = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise ValueError("Every benchmark case needs a string id.")
        if case["id"] in ids:
            raise ValueError(f"Duplicate benchmark id: {case['id']}")
        ids.add(case["id"])
        kind = case.get("kind")
        review = case.get("review_status")
        if kind not in VALID_KINDS or review not in VALID_REVIEWS:
            raise ValueError(f"{case['id']}: invalid kind or review_status.")
        if not case.get("language") or not case.get("genre"):
            raise ValueError(f"{case['id']}: language and genre are required.")
        if review == "native-reviewed" and not all(
            case.get(field) for field in ("reviewer", "annotation_date", "source_provenance")
        ):
            raise ValueError(f"{case['id']}: native-reviewed cases require reviewer, annotation_date, and source_provenance.")
        if kind == "serious-detection":
            if not isinstance(case.get("expected"), bool):
                raise ValueError(f"{case['id']}: expected must be boolean.")
            actual = detect_serious_document(case["text"], case.get("document_type", "auto"))[0]
        else:
            if case.get("expected") not in {"pass-exact", "needs-review", "fail-literal"}:
                raise ValueError(f"{case['id']}: invalid fidelity expectation.")
            actual = compare_fidelity(case["source"], case["candidate"]).status
        rows.append({
            "id": case["id"], "kind": kind, "language": case["language"],
            "genre": case["genre"], "review_status": review,
            "expected": case["expected"], "actual": actual,
            "passed": actual == case["expected"],
        })
    groups = {}
    for review in VALID_REVIEWS:
        group = [row for row in rows if row["review_status"] == review]
        serious = [row for row in group if row["kind"] == "serious-detection"]
        tp = sum(row["expected"] and row["actual"] for row in serious)
        fp = sum(not row["expected"] and row["actual"] for row in serious)
        fn = sum(row["expected"] and not row["actual"] for row in serious)
        tn = sum(not row["expected"] and not row["actual"] for row in serious)
        groups[review] = {
            "total": len(group), "passed": sum(row["passed"] for row in group),
            "serious_detection": {
                "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                "precision": round(tp / (tp + fp), 3) if tp + fp else None,
                "recall": round(tp / (tp + fn), 3) if tp + fn else None,
            },
        }
    strata = {}
    for row in rows:
        key = f"{row['language']} / {row['genre']} / {row['review_status']}"
        entry = strata.setdefault(key, {"total": 0, "passed": 0})
        entry["total"] += 1
        entry["passed"] += row["passed"]
    return {
        "cases": rows,
        "groups": groups,
        "strata": strata,
        "disclaimer": (
            "Seed cases are developer-written smoke tests, not independent native-speaker validation. "
            "Only native-reviewed cases can support external quality claims; even then, report by language and genre."
        ),
    }


def format_evaluation(report: dict, output_format: str = "markdown") -> str:
    if output_format == "json":
        return json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    lines = ["# Writing Quality Benchmark", "", report["disclaimer"], ""]
    for status, group in report["groups"].items():
        metrics = group["serious_detection"]
        lines.extend([
            f"## {status}",
            f"- Cases passed: {group['passed']}/{group['total']}",
            f"- Serious detection: TP {metrics['tp']}, FP {metrics['fp']}, FN {metrics['fn']}, TN {metrics['tn']}",
            f"- Precision: {metrics['precision']}; recall: {metrics['recall']}", "",
        ])
    lines.extend(["## By language and genre", ""])
    lines.extend(
        f"- {key}: {entry['passed']}/{entry['total']}"
        for key, entry in sorted(report["strata"].items())
    )
    lines.append("")
    failures = [row for row in report["cases"] if not row["passed"]]
    lines.append("## Mismatches")
    lines.extend(f"- {row['id']} ({row['language']}, {row['genre']}): expected {row['expected']}, got {row['actual']}" for row in failures)
    if not failures:
        lines.append("- none in this fixture set")
    return "\n".join(lines) + "\n"
