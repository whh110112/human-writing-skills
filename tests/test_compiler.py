import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from humanwriting.cli import main
from humanwriting.compiler import compile_audit_prompt, compile_prompt
from humanwriting.detection import detect_audit_profiles
from humanwriting.pipeline import write_audit_pipeline
from humanwriting.skills import (
    default_skills_dir,
    list_module_skills,
    list_skills,
    list_style_skills,
    load_skill,
)


class CompilerTests(unittest.TestCase):
    def test_lists_builtin_skills(self):
        skills = list_skills()
        self.assertIn("fiction", skills)
        self.assertIn("webnovel", skills)

    def test_default_skills_resource_contains_core_files(self):
        root = default_skills_dir()
        self.assertTrue(root.joinpath("fiction.md").is_file())
        self.assertTrue(root.joinpath("relationship-stance-audit.md").is_file())

    def test_lists_style_and_module_skills(self):
        self.assertIn("fiction", list_style_skills())
        self.assertIn("embodied-emotion", list_module_skills())
        self.assertIn("narrative-bridges", list_module_skills())
        self.assertIn("relationship-state", list_module_skills())
        self.assertIn("natural-measurement", list_module_skills())
        self.assertIn("forensic-physical-audit", list_module_skills())
        self.assertIn("occupancy-capacity", list_module_skills())
        self.assertIn("relationship-stance-audit", list_module_skills())
        self.assertIn("cliche-phrase-audit", list_module_skills())
        self.assertIn("formulaic-structure-audit", list_module_skills())
        self.assertIn("prose-progress-audit", list_module_skills())
        self.assertIn("logic-causality-audit", list_module_skills())
        self.assertIn("character-consistency-audit", list_module_skills())
        self.assertIn("proofreading-audit", list_module_skills())
        self.assertIn("reference-style-alignment", list_module_skills())
        self.assertIn("dialogue-voice-audit", list_module_skills())
        self.assertIn("serial-reentry", list_module_skills())
        self.assertIn("narrative-distance-control", list_module_skills())
        self.assertIn("imagery-load-audit", list_module_skills())
        self.assertIn("paragraph-rhythm-audit", list_module_skills())
        self.assertIn("detail-disclosure-audit", list_module_skills())

    def test_load_skill_content(self):
        skill = load_skill("news-report")
        self.assertEqual(skill.name, "news-report")
        self.assertEqual(skill.kind, "style")
        self.assertIn("News Report Skill", skill.content)

    def test_compile_prompt_contains_style_and_task(self):
        prompt = compile_prompt("fiction", "Write the next scene.")
        self.assertIn("Core Directive", prompt)
        self.assertIn("Beat bridge", prompt)
        self.assertIn("Relationship state", prompt)
        self.assertIn("Fiction Skill", prompt)
        self.assertIn("Write the next scene.", prompt)
        self.assertNotIn("Technique Module: reference-style-alignment", prompt)

    def test_reference_style_does_not_activate_without_explicit_signal(self):
        prompt = compile_prompt("fiction", "Write a quiet scene by the river.")
        self.assertNotIn("Technique Module: reference-style-alignment", prompt)
        self.assertNotIn("Reference Style Material", prompt)

    def test_explicit_task_style_request_activates_reference_module(self):
        prompt = compile_prompt("fiction", "参考冷峻克制的文风写下一场戏。")
        self.assertIn("Technique Module: reference-style-alignment", prompt)
        self.assertIn("Reference Style Material", prompt)
        self.assertIn("参考冷峻克制的文风", prompt)

    def test_reference_file_activates_and_respects_sampling_budget(self):
        with TemporaryDirectory() as directory:
            reference = Path(directory) / "reference.md"
            reference.write_text("甲" * 6000 + "中段标记" + "乙" * 6000, encoding="utf-8")
            prompt = compile_prompt(
                "fiction",
                "Write the next scene.",
                reference_paths=[str(reference)],
                reference_budget=1200,
            )
        self.assertIn("Technique Module: reference-style-alignment", prompt)
        self.assertIn("Reference: reference.md", prompt)
        self.assertIn("middle sample", prompt)
        self.assertLess(prompt.count("甲") + prompt.count("乙"), 1400)

    def test_many_reference_files_share_one_global_budget(self):
        with TemporaryDirectory() as directory:
            paths = []
            for index in range(12):
                path = Path(directory) / f"reference-{index}.md"
                path.write_text(str(index) * 2000, encoding="utf-8")
                paths.append(str(path))
            from humanwriting.reference import build_reference_pack

            pack = build_reference_pack(paths=paths, budget=1000)
        self.assertLessEqual(pack.sampled_characters, 1000)

    def test_audit_reference_automatically_adds_style_match(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            reference = root / "reference.md"
            draft.write_text("她推开门，没有回头。", encoding="utf-8")
            reference.write_text("雨落得很慢。灯没有亮。", encoding="utf-8")
            prompt = compile_audit_prompt(
                str(draft),
                profiles=["character"],
                reference_paths=[str(reference)],
            )
        self.assertIn("Selected profiles: character, style-match", prompt)
        self.assertIn("Audit Module: reference-style-alignment", prompt)
        self.assertIn("Reference: reference.md", prompt)

    def test_style_match_profile_requires_explicit_reference(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("A short draft.", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "requires --reference"):
                compile_audit_prompt(str(draft), profiles=["style-match"])

    def test_compile_prompt_can_add_modules(self):
        prompt = compile_prompt(
            "fiction",
            "Write the next scene.",
            modules=[
                "narrative-bridges",
                "relationship-state",
                "natural-measurement",
                "embodied-emotion",
                "vocal-rhythm",
            ],
            review=True,
        )
        self.assertIn("Technique Module: narrative-bridges", prompt)
        self.assertIn("Technique Module: relationship-state", prompt)
        self.assertIn("Technique Module: natural-measurement", prompt)
        self.assertIn("Technique Module: embodied-emotion", prompt)
        self.assertIn("Technique Module: vocal-rhythm", prompt)
        self.assertIn("Technique Module: editor-loop", prompt)
        self.assertIn("Technique Module: ai-trace-rubric", prompt)
        self.assertNotIn("Technique Module: relationship-stance-audit", prompt)
        self.assertNotIn("Technique Module: cliche-phrase-audit", prompt)
        self.assertNotIn("Technique Module: formulaic-structure-audit", prompt)
        self.assertNotIn("Technique Module: prose-progress-audit", prompt)

    def test_deep_review_adds_detailed_audits_and_is_larger(self):
        compact = compile_prompt("fiction", "Write the next scene.", review=True)
        deep = compile_prompt("fiction", "Write the next scene.", deep_review=True)
        self.assertIn("Technique Module: cliche-phrase-audit", deep)
        self.assertIn("Technique Module: formulaic-structure-audit", deep)
        self.assertIn("Technique Module: prose-progress-audit", deep)
        self.assertIn("Technique Module: relationship-stance-audit", deep)
        self.assertIn("Technique Module: natural-measurement", deep)
        self.assertLess(len(compact), len(deep))
        self.assertNotIn("Technique Module: dialogue-voice-audit", deep)
        self.assertNotIn("Technique Module: serial-reentry", deep)
        self.assertNotIn("Technique Module: imagery-load-audit", deep)

    def test_new_generation_modules_are_explicit_and_independent(self):
        prompt = compile_prompt(
            "fiction",
            "Write a dialogue scene.",
            modules=["dialogue-voice-audit", "paragraph-rhythm-audit"],
        )
        self.assertIn("Technique Module: dialogue-voice-audit", prompt)
        self.assertIn("Technique Module: paragraph-rhythm-audit", prompt)
        self.assertNotIn("Technique Module: serial-reentry", prompt)
        self.assertNotIn("Technique Module: imagery-load-audit", prompt)

    def test_compact_review_stays_within_generation_prompt_budget(self):
        context = Path(__file__).resolve().parent.parent / "examples" / "story-ledger.md"
        prompt = compile_prompt(
            "webnovel",
            "Continue the next chapter.",
            context_path=str(context),
            review=True,
            strict_continuity=True,
        )
        self.assertLess(len(prompt), 22000)

    def test_duplicate_modules_are_loaded_once(self):
        prompt = compile_prompt(
            "fiction",
            "Write the next scene.",
            modules=["vocal-rhythm", "vocal-rhythm"],
        )
        self.assertEqual(prompt.count("# Technique Module: vocal-rhythm"), 1)

    def test_only_deep_review_adds_number_sense_for_narrative_styles(self):
        fiction_prompt = compile_prompt("fiction", "Write the next scene.", review=True)
        deep_fiction_prompt = compile_prompt("fiction", "Write the next scene.", deep_review=True)
        deep_news_prompt = compile_prompt("news-report", "Write the report.", deep_review=True)
        self.assertNotIn("Technique Module: natural-measurement", fiction_prompt)
        self.assertIn("Technique Module: natural-measurement", deep_fiction_prompt)
        self.assertNotIn("Technique Module: natural-measurement", deep_news_prompt)

    def test_number_sense_can_be_explicitly_added(self):
        prompt = compile_prompt("news-report", "Write the report.", number_sense=True)
        self.assertIn("Technique Module: natural-measurement", prompt)

    def test_compile_prompt_can_add_strict_continuity_modules(self):
        prompt = compile_prompt(
            "fiction",
            "Write a car scene.",
            strict_continuity=True,
        )
        self.assertIn("Technique Module: occupancy-capacity", prompt)
        self.assertIn("Technique Module: spatial-blocking", prompt)
        self.assertIn("Technique Module: appearance-prop-continuity", prompt)
        self.assertNotIn("Technique Module: physical-continuity-audit", prompt)

    def test_compile_audit_prompt_extracts_draft_and_modules(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text(
                "Lao Gao looked from the front row toward Yanzi behind the glass. "
                "Later, he touched Yanzi in the rear seat. Yanzi wore flats, then heels.",
                encoding="utf-8",
            )
            prompt = compile_audit_prompt(str(draft), number_sense=True)
        self.assertIn("Audit Directive", prompt)
        self.assertIn("Audit Module: forensic-physical-audit", prompt)
        self.assertIn("Audit Module: occupancy-capacity", prompt)
        self.assertIn("Audit Module: spatial-blocking", prompt)
        self.assertIn("Audit Module: relationship-stance-audit", prompt)
        self.assertIn("Audit Module: cliche-phrase-audit", prompt)
        self.assertIn("Audit Module: formulaic-structure-audit", prompt)
        self.assertIn("Audit Module: prose-progress-audit", prompt)
        self.assertIn("Audit Module: natural-measurement", prompt)
        self.assertIn("Audit Module: logic-causality-audit", prompt)
        self.assertIn("Audit Module: character-consistency-audit", prompt)
        self.assertIn("Audit Module: proofreading-audit", prompt)
        self.assertIn("Draft To Audit", prompt)
        self.assertIn("behind the glass", prompt)
        self.assertIn("flats, then heels", prompt)

    def test_no_strict_continuity_removes_all_physical_audits(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("A said B was trustworthy.", encoding="utf-8")
            prompt = compile_audit_prompt(str(draft), strict_continuity=False)
        self.assertNotIn("Audit Module: forensic-physical-audit", prompt)
        self.assertNotIn("Audit Module: physical-continuity-audit", prompt)
        self.assertNotIn("forensic physical continuity audit", prompt)
        self.assertIn("Audit Module: relationship-stance-audit", prompt)
        self.assertIn("Audit Module: ai-trace-rubric", prompt)

    def test_full_audit_does_not_load_optional_high_cost_profiles(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("她说：\u201c回来。\u201d他答：\u201c不。\u201d", encoding="utf-8")
            prompt = compile_audit_prompt(str(draft))
        self.assertNotIn("Audit Module: dialogue-voice-audit", prompt)
        self.assertNotIn("Audit Module: serial-reentry", prompt)
        self.assertNotIn("Audit Module: imagery-load-audit", prompt)

    def test_relationship_profile_does_not_load_unrelated_audits(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("A praised C in front of B.", encoding="utf-8")
            prompt = compile_audit_prompt(str(draft), profiles=["relationship"])
        self.assertIn("Audit Module: relationship-state", prompt)
        self.assertIn("Audit Module: relationship-stance-audit", prompt)
        self.assertNotIn("Audit Module: forensic-physical-audit", prompt)
        self.assertNotIn("Audit Module: ai-trace-rubric", prompt)

    def test_numbers_profile_only_loads_number_audit(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("Her hand moved three centimeters.", encoding="utf-8")
            prompt = compile_audit_prompt(str(draft), profiles=["numbers"])
        self.assertIn("Audit Module: natural-measurement", prompt)
        self.assertNotIn("Audit Module: forensic-physical-audit", prompt)
        self.assertNotIn("Audit Module: ai-trace-rubric", prompt)

    def test_logic_character_and_proofread_profiles_are_isolated(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("A decision caused a later consequence.", encoding="utf-8")
            logic = compile_audit_prompt(str(draft), profiles=["logic"])
            character = compile_audit_prompt(str(draft), profiles=["character"])
            proofread = compile_audit_prompt(str(draft), profiles=["proofread"])
        self.assertIn("Audit Module: logic-causality-audit", logic)
        self.assertNotIn("Audit Module: character-consistency-audit", logic)
        self.assertIn("Audit Module: character-consistency-audit", character)
        self.assertNotIn("Audit Module: logic-causality-audit", character)
        self.assertIn("Audit Module: proofreading-audit", proofread)
        self.assertNotIn("Audit Module: ai-trace-rubric", proofread)

    def test_voice_serial_and_texture_profiles_are_isolated(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            context = root / "ledger.md"
            draft.write_text("她说：\u201c别问。\u201d他答：\u201c我必须问。\u201d", encoding="utf-8")
            context.write_text("上一章结束时，两人仍在车站。", encoding="utf-8")
            voice = compile_audit_prompt(str(draft), profiles=["voice"])
            serial = compile_audit_prompt(
                str(draft),
                context_path=str(context),
                profiles=["serial"],
            )
            texture = compile_audit_prompt(str(draft), profiles=["texture"])
        self.assertIn("Audit Module: dialogue-voice-audit", voice)
        self.assertNotIn("Audit Module: serial-reentry", voice)
        self.assertIn("Audit Module: serial-reentry", serial)
        self.assertNotIn("Audit Module: dialogue-voice-audit", serial)
        self.assertIn("Audit Module: imagery-load-audit", texture)
        self.assertIn("Audit Module: paragraph-rhythm-audit", texture)
        self.assertNotIn("Audit Module: dialogue-voice-audit", texture)

    def test_serial_profile_requires_prior_context(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("第二章开始了。", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "requires --context"):
                compile_audit_prompt(str(draft), profiles=["serial"])

    def test_auto_detection_keeps_core_and_skips_irrelevant_optional_stages(self):
        decisions = detect_audit_profiles(
            "This report evaluates policy outcomes and presents a cautious conclusion."
        )
        selected = {decision.profile for decision in decisions if decision.selected}
        self.assertEqual(selected, {"logic", "ai-trace", "proofread"})

    def test_auto_detection_selects_scene_specific_stages(self):
        decisions = detect_audit_profiles("她坐在后排说：董事长已经等了七秒。")
        selected = {decision.profile for decision in decisions if decision.selected}
        self.assertEqual(
            selected,
            {"logic", "character", "relationship", "physical", "ai-trace", "numbers", "proofread"},
        )

    def test_auto_detection_adds_new_profiles_only_on_matching_cues(self):
        draft = (
            "第二章。\n\n"
            "她说：\u201c你又迟到了。\u201d\n\n"
            "他低声答：\u201c路上出了事。\u201d\n\n"
            "她问：\u201c什么事？\u201d\n\n"
            "他说：\u201c现在不能讲。\u201d\n\n"
            "灯像一只眼睛，雨像旧胶片，门仿佛在喘气，走廊如同一条空船，夜色好似潮水。"
        )
        decisions = detect_audit_profiles(draft, context_active=True)
        selected = {decision.profile for decision in decisions if decision.selected}
        self.assertTrue({"voice", "serial", "texture"} <= selected)

    def test_auto_detection_skips_serial_without_context(self):
        decisions = detect_audit_profiles("第二章，他想起上一章的争执。")
        selected = {decision.profile for decision in decisions if decision.selected}
        self.assertNotIn("serial", selected)

    def test_pipeline_writes_independent_stage_prompts_and_manifest(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            output = root / "pipeline"
            draft.write_text("她坐在后排说：董事长已经等了七秒。", encoding="utf-8")
            written, stages = write_audit_pipeline(
                str(draft),
                str(output),
                auto=True,
            )
            logic_prompt = (written / "01-logic.md").read_text(encoding="utf-8")
            manifest = (written / "README.md").read_text(encoding="utf-8")
            lint_report = (written / "00-pattern-lint.json").read_text(encoding="utf-8")
        self.assertEqual(len(stages), 7)
        self.assertIn("Audit Module: logic-causality-audit", logic_prompt)
        self.assertNotIn("Audit Module: character-consistency-audit", logic_prompt)
        self.assertIn("fresh model conversation", manifest)
        self.assertIn("Detected exact-number cue", manifest)
        self.assertIn("Pattern lint style", manifest)
        self.assertIn('"disclaimer"', lint_report)

    def test_pipeline_adds_style_match_only_with_reference(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            reference = root / "reference.md"
            draft.write_text("一份没有人物动作的说明文本。", encoding="utf-8")
            reference.write_text("句子很短。偶尔很长，但不解释。", encoding="utf-8")
            without_reference, _ = write_audit_pipeline(
                str(draft),
                str(root / "without-reference"),
                auto=True,
            )
            with_reference, stages = write_audit_pipeline(
                str(draft),
                str(root / "with-reference"),
                auto=True,
                reference_paths=[str(reference)],
            )
            without_manifest = (without_reference / "README.md").read_text(encoding="utf-8")
            with_manifest = (with_reference / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("| `style-match` | yes |", without_manifest)
        self.assertIn("| `style-match` | yes |", with_manifest)
        self.assertIn("style-match", [stage.profile for stage in stages])

    def test_cli_reports_missing_draft_without_traceback(self):
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            main(["audit", "--draft", "missing-draft.md"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("missing-draft.md", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
