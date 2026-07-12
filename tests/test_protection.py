import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from humanwriting.compiler import compile_audit_prompt, compile_prompt
from humanwriting.protection import (
    build_protection_manifest,
    compare_protected_content,
    extract_protected_items,
)


class ProtectionTests(unittest.TestCase):
    def test_extracts_numbers_citations_urls_code_and_terms(self):
        text = "Accuracy was 92.4% [12]. See https://example.com and run `train.py`."
        items = extract_protected_items(text, terms=["Accuracy"])
        kinds = {item.kind for item in items}
        self.assertTrue({"number", "citation", "url", "inline-code", "explicit-term"} <= kinds)
        values = {(item.kind, item.value) for item in items}
        self.assertNotIn(("number", "12"), values)

    def test_verification_fails_when_fact_or_citation_changes(self):
        source = "Accuracy was 92.4% [12]."
        candidate = "Accuracy was 94.2% [13]."
        report = compare_protected_content(source, candidate)
        self.assertFalse(report.ok)
        missing_values = {item.value for item in report.missing_or_changed}
        self.assertIn("92.4%", missing_values)
        self.assertIn("[12]", missing_values)
        self.assertIn("94.2%", {item.value for item in report.added})

    def test_verification_passes_when_surrounding_prose_changes(self):
        source = "The result was 92.4% [12], which is important."
        candidate = "The measured accuracy remained 92.4% [12]."
        report = compare_protected_content(source, candidate)
        self.assertTrue(report.ok)

    def test_verification_fails_when_candidate_invents_protected_value(self):
        report = compare_protected_content("No measured value.", "The value was 17.2%.")
        self.assertFalse(report.ok)
        self.assertIn("17.2%", {item.value for item in report.added})

    def test_manifest_lists_explicit_term_even_before_generation(self):
        manifest = build_protection_manifest("", terms=["Salt Office"])
        self.assertIn("Salt Office", manifest)

    def test_build_and_audit_activate_protection_only_when_requested(self):
        plain = compile_prompt("fiction", "Write the next scene.")
        protected = compile_prompt(
            "fiction",
            "Write the next scene.",
            protect_terms=["Salt Office"],
        )
        self.assertNotIn("Technique Module: protected-content", plain)
        self.assertIn("Technique Module: protected-content", protected)
        self.assertIn("Salt Office", protected)

        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("Accuracy was 92.4% [12].", encoding="utf-8")
            audit = compile_audit_prompt(
                str(draft),
                profiles=["proofread"],
                protect_content=True,
            )
        self.assertIn("Audit Module: protected-content", audit)
        self.assertIn("Protected Content Manifest", audit)
        self.assertIn("92.4%", audit)
        self.assertIn("[12]", audit)


if __name__ == "__main__":
    unittest.main()
