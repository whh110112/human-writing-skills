from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path


SEVERITY_WEIGHT = {"low": 2, "medium": 5, "high": 9}
NARRATIVE_STYLES = {"fiction", "webnovel", "self-media"}
CHAPTER_HEADING_PATTERN = re.compile(
    r"(?m)^\s*(?:#{1,6}\s*)?(?:第\s*[一二三四五六七八九十百零〇\d]+\s*[章节回卷]|"
    r"chapter\s+\d+)[^\n]*$",
    re.IGNORECASE,
)
SCENE_OPENING_CUE_PATTERNS = {
    "clock": re.compile(
        r"(?:(?:凌晨|清晨|早上|上午|中午|下午|傍晚|晚上|夜里)\s*"
        r"(?:\d{1,2}|[一二三四五六七八九十两]+)\s*(?:点|时)(?:半|\d{1,2}分)?|"
        r"(?:\d{1,2}|[一二三四五六七八九十两]+)\s*点(?:半|\d{1,2}分)?|"
        r"\d{1,2}\s*时(?:\d{1,2}分)?)"
    ),
    "place": re.compile(
        r"[\u4e00-\u9fffA-Za-z0-9]{2,18}(?:机场|航站楼|车站|酒店|大厦|公寓|办公室|"
        r"宿舍|宫殿|广场|餐厅|咖啡馆|会所|小区|街口|路口|码头|医院|学校)"
    ),
    "light-weather": re.compile(
        r"落日|夕阳|阳光|晨光|暮色|夜色|灯光|月光|雨|雪|雾|夜风|微风|冷风"
    ),
    "appearance": re.compile(
        r"身穿|穿着|外套|短裙|长裙|西装|制服|高跟鞋|平底鞋|长发|短发|妆容"
    ),
    "generalized-feeling": re.compile(
        r"莫名|说不清|无法形容|不知为何|不知道为什么|一股.{0,16}(?:感觉|情绪)|"
        r"(?:疲惫|紧张|幸福|不安|心动)中带着?"
    ),
}
FORMULAIC_INTROSPECTION_PATTERN = re.compile(
    r"不是那种.{0,45}而是|像是.{0,35}(?:又像是|却又像)|"
    r"(?:他|她|我)不知道为什么|(?:他|她|我)?莫名(?:地|其妙|就)?|"
    r"说不清(?:是什么|为什么)|无法形容(?:的|这种)"
)


@dataclass(frozen=True)
class PatternRule:
    rule_id: str
    category: str
    severity: str
    pattern: re.Pattern[str]
    message: str
    excluded_styles: frozenset[str] = frozenset()


@dataclass(frozen=True)
class LintFinding:
    rule_id: str
    category: str
    severity: str
    line: int
    column: int
    start: int
    end: int
    excerpt: str
    message: str


@dataclass(frozen=True)
class LintReport:
    score: int
    label: str
    confidence: str
    style: str
    character_count: int
    word_count: int
    findings: tuple[LintFinding, ...]
    disclaimer: str = (
        "This is a writing-pattern score, not evidence of AI authorship. "
        "Human writing can trigger the same patterns."
    )

    def to_dict(self) -> dict:
        result = asdict(self)
        result["findings"] = [asdict(finding) for finding in self.findings]
        return result


RULES = [
    PatternRule(
        "LEX001",
        "inflated-vocabulary",
        "medium",
        re.compile(
            r"\b(?:delve|tapestry|realm|pivotal|groundbreaking|transformative|"
            r"seamless|game[- ]changer|ever[- ]evolving|testament to)\b",
            re.IGNORECASE,
        ),
        "Replace abstract prestige language with a specific fact, action, or consequence.",
    ),
    PatternRule(
        "LEX002",
        "inflated-vocabulary",
        "medium",
        re.compile(r"命运的齿轮(?:已经)?(?:开始)?转动|时代的洪流|历史的车轮|一场风暴即将来临"),
        "Fate inflation announces importance instead of putting an irreversible change on the page.",
    ),
    PatternRule(
        "BODY001",
        "generic-body-cue",
        "medium",
        re.compile(r"嘴角微微(?:上扬|勾起)|眼中闪过一丝|深邃的眼眸|眸光微闪|眉头微皱"),
        "Generic body language should be replaced with character- and situation-specific behavior.",
    ),
    PatternRule(
        "EMO001",
        "emotion-label",
        "medium",
        re.compile(r"不禁感到一阵|心中涌起(?:一股|一阵)?复杂(?:的)?情绪|百感交集"),
        "Show the emotion through action, perception, contradiction, or consequence.",
    ),
    PatternRule(
        "EMO002",
        "show-then-gloss",
        "medium",
        re.compile(
            r"(?:握紧|攥紧|避开(?:了)?目光|垂下(?:了)?眼|停住(?:了)?脚步|"
            r"手指(?:微微)?发抖|呼吸(?:一滞|急促)).{0,60}?"
            r"(?:这表明|显然|说明|因为|感到|意味着).{0,20}?"
            r"(?:愤怒|紧张|害怕|犹豫|不安|羞愧|嫉妒|悲伤)",
            re.DOTALL,
        ),
        "The action already carries the emotion; remove the gloss unless it complicates or corrects the evidence.",
        excluded_styles=frozenset({"academic-paper", "news-report"}),
    ),
    PatternRule(
        "ATM001",
        "empty-atmosphere",
        "medium",
        re.compile(r"空气仿佛凝固|时间在这一刻静止|气氛(?:顿时|瞬间)?变得凝重"),
        "Replace generic atmosphere with a local sound, object, movement, or social reaction.",
    ),
    PatternRule(
        "STR001",
        "formulaic-contrast",
        "high",
        re.compile(
            r"(?:不只是|不仅仅是|不是).{1,80}?(?:而是|更是)|"
            r"\b(?:it|this) (?:is|isn't|is not) not just .{1,100}?\bbut\b|"
            r"\bnot just .{1,100}?\bbut also\b",
            re.IGNORECASE,
        ),
        "State the actual claim directly instead of using a not-X-but-Y reveal.",
    ),
    PatternRule(
        "TRANS001",
        "dead-transition",
        "low",
        re.compile(
            r"(?:值得注意的是|需要指出的是|综上所述|总而言之|与此同时)|"
            r"\b(?:moreover|furthermore|it is important to note|in conclusion|to summarize)\b",
            re.IGNORECASE,
        ),
        "Check whether the transition carries real causality or only announces structure.",
        excluded_styles=frozenset({"academic-paper", "news-report"}),
    ),
    PatternRule(
        "OPEN001",
        "generic-opening",
        "medium",
        re.compile(
            r"在当今(?:快速发展|瞬息万变|日新月异)的|随着.{0,20}的不断发展|"
            r"\bin today['’]s (?:fast-paced|rapidly evolving) world\b|\blet['’]s dive in\b",
            re.IGNORECASE,
        ),
        "Open with the subject, event, conflict, or evidence instead of generic scene-setting.",
    ),
    PatternRule(
        "CLOSE001",
        "generic-conclusion",
        "medium",
        re.compile(
            r"未来可期|让我们拭目以待|相信在不久的将来|"
            r"\b(?:the future looks bright|only time will tell|exciting times lie ahead)\b",
            re.IGNORECASE,
        ),
        "Replace the generic optimistic ending with a specific next action, limit, or unresolved pressure.",
    ),
    PatternRule(
        "CHAT001",
        "chatbot-artifact",
        "high",
        re.compile(
            r"希望这对你有所帮助|如果你愿意，我可以|如有其他问题，请随时|"
            r"\b(?:I hope this helps|let me know if you(?:'d| would) like|feel free to ask)\b",
            re.IGNORECASE,
        ),
        "Remove assistant-style offer-to-continue language from finished prose.",
    ),
    PatternRule(
        "PROMO001",
        "promotional-language",
        "medium",
        re.compile(
            r"令人叹为观止|无缝(?:衔接|体验|集成)|充满活力的|极具创新性的|"
            r"\b(?:breathtaking|cutting-edge|unlock the potential|vibrant ecosystem)\b",
            re.IGNORECASE,
        ),
        "Replace promotional adjectives with observable proof.",
    ),
    PatternRule(
        "HEDGE001",
        "stacked-hedging",
        "medium",
        re.compile(
            r"(?:可能|或许|大概).{0,12}(?:可能|或许|大概)|"
            r"\b(?:could potentially|may perhaps|might possibly)\b",
            re.IGNORECASE,
        ),
        "Keep one calibrated hedge and remove the stack.",
    ),
    PatternRule(
        "PREC001",
        "false-precision",
        "low",
        re.compile(
            r"(?:\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万点]+)\s*"
            r"(?:毫米|厘米|秒|次|mm|cm|seconds?|times?)",
            re.IGNORECASE,
        ),
        "Verify that the narrator or character has a reason to know this exact micro-measurement.",
        excluded_styles=frozenset({"academic-paper", "news-report"}),
    ),
]


MASK_PATTERNS = [
    re.compile(r"```.*?```", re.DOTALL),
    re.compile(r"`[^`\n]+`"),
    re.compile(r"(?m)^\s*>.*$"),
    re.compile(r"https?://\S+"),
]


def _mask_ignored_regions(text: str) -> str:
    chars = list(text)
    for pattern in MASK_PATTERNS:
        for match in pattern.finditer(text):
            for index in range(match.start(), match.end()):
                if chars[index] not in "\r\n":
                    chars[index] = " "
    return "".join(chars)


def _line_column(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    previous_newline = text.rfind("\n", 0, offset)
    column = offset - previous_newline
    return line, column


def _finding_from_span(
    text: str,
    rule_id: str,
    category: str,
    severity: str,
    start: int,
    end: int,
    message: str,
) -> LintFinding:
    line, column = _line_column(text, start)
    excerpt = text[start:end].replace("\n", " ").strip()
    return LintFinding(rule_id, category, severity, line, column, start, end, excerpt, message)


def _sentence_lengths(text: str) -> list[int]:
    sentences = [part.strip() for part in re.split(r"[。！？.!?]+", text) if part.strip()]
    return [len(re.findall(r"[\u4e00-\u9fff]|\b[\w'-]+\b", sentence)) for sentence in sentences]


def _paragraph_spans(text: str) -> list[tuple[int, int, str]]:
    return [
        (match.start(), match.end(), match.group(0).strip())
        for match in re.finditer(r"\S.*?(?=\n\s*\n|\Z)", text, re.DOTALL)
        if match.group(0).strip()
    ]


def _coefficient_of_variation(values: list[int]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance) / mean


def _chapter_opening_spans(text: str, width: int = 700) -> list[tuple[int, int]]:
    return [
        (match.end(), min(len(text), match.end() + width))
        for match in CHAPTER_HEADING_PATTERN.finditer(text)
    ]


def _scene_opening_cues(fragment: str) -> set[str]:
    return {
        name
        for name, pattern in SCENE_OPENING_CUE_PATTERNS.items()
        if pattern.search(fragment)
    }


def _precision_is_earned(text: str, start: int, end: int) -> bool:
    context = text[max(0, start - 60) : min(len(text), end + 60)]
    return bool(
        re.search(
            r"法医|鉴定|伤口|病历|医学|检验|检测|测量|仪器|报告|工程|参数|规格|"
            r"实验|数据|证据|建筑高度|剂量|病例|"
            r"\b(?:forensic|medical|wound|measured|measurement|report|engineering|"
            r"specification|experiment|evidence|dosage)\b",
            context,
            re.IGNORECASE,
        )
    )


def lint_text(
    text: str,
    style: str = "general",
    allow: set[str] | None = None,
) -> LintReport:
    allowed = allow or set()
    masked = _mask_ignored_regions(text)
    findings: list[LintFinding] = []
    for rule in RULES:
        if style in rule.excluded_styles or rule.rule_id in allowed or rule.category in allowed:
            continue
        if rule.rule_id == "PREC001" and style not in NARRATIVE_STYLES:
            continue
        for match in rule.pattern.finditer(masked):
            if rule.rule_id == "PREC001" and _precision_is_earned(
                masked,
                match.start(),
                match.end(),
            ):
                continue
            findings.append(
                _finding_from_span(
                    text,
                    rule.rule_id,
                    rule.category,
                    rule.severity,
                    match.start(),
                    match.end(),
                    rule.message,
                )
            )

    sentence_lengths = _sentence_lengths(masked)
    if len(sentence_lengths) >= 5 and _coefficient_of_variation(sentence_lengths) < 0.16:
        findings.append(
            _finding_from_span(
                text,
                "RHYTHM001",
                "uniform-rhythm",
                "medium",
                0,
                min(len(text), 120),
                "Sentence lengths are unusually uniform; vary cadence where the genre permits.",
            )
        )

    em_dash_count = masked.count("—")
    word_count = len(re.findall(r"[\u4e00-\u9fff]|\b[\w'-]+\b", masked))
    if em_dash_count >= 3 and em_dash_count * 500 > max(word_count, 1):
        first_dash = masked.find("—")
        findings.append(
            _finding_from_span(
                text,
                "PUNCT001",
                "dash-density",
                "low",
                first_dash,
                first_dash + 1,
                "Em-dash density is high; verify that each dash marks a real interruption or turn.",
            )
        )

    if style in NARRATIVE_STYLES:
        paragraphs = _paragraph_spans(masked)
        imagery_pattern = re.compile(
            r"像|仿佛|如同|宛如|好似|犹如|\blike\b|\bas if\b",
            re.IGNORECASE,
        )
        detail_pattern = re.compile(
            r"(?:[今现]年)?\d{1,3}岁|身高|体重|职业|结婚[了]?\d|任职|毕业于|"
            r"\b(?:aged?|height|weighs?|occupation|married|graduated)\b",
            re.IGNORECASE,
        )
        for start, end, paragraph in paragraphs:
            image_count = len(imagery_pattern.findall(paragraph))
            if (
                image_count >= 4
                and "IMG001" not in allowed
                and "imagery-density" not in allowed
            ):
                findings.append(
                    _finding_from_span(
                        text,
                        "IMG001",
                        "imagery-density",
                        "medium",
                        start,
                        min(end, start + 160),
                        "This paragraph stacks several comparisons; keep the image that changes perception or action.",
                    )
                )
            detail_count = len(detail_pattern.findall(paragraph))
            if (
                detail_count >= 3
                and "INFO001" not in allowed
                and "detail-inventory" not in allowed
            ):
                findings.append(
                    _finding_from_span(
                        text,
                        "INFO001",
                        "detail-inventory",
                        "medium",
                        start,
                        min(end, start + 160),
                        "Several biographical or measured details arrive together; keep what the scene uses and delay the rest.",
                    )
                )

        opening_spans = [(0, min(len(masked), 700)), *_chapter_opening_spans(masked)]
        seen_starts: set[int] = set()
        stacked_openings: list[tuple[int, int, set[str]]] = []
        for start, end in opening_spans:
            if start in seen_starts:
                continue
            seen_starts.add(start)
            cues = _scene_opening_cues(masked[start:end])
            if len(cues) >= 4:
                stacked_openings.append((start, end, cues))
        if "OPEN002" not in allowed and "cinematic-opening-stack" not in allowed:
            for start, end, cues in stacked_openings[:3]:
                findings.append(
                    _finding_from_span(
                        text,
                        "OPEN002",
                        "cinematic-opening-stack",
                        "medium",
                        start,
                        min(end, start + 180),
                        "The opening front-loads "
                        + ", ".join(sorted(cues))
                        + "; keep only details used by the first pressure-bearing action.",
                    )
                )

        introspection_matches = list(FORMULAIC_INTROSPECTION_PATTERN.finditer(masked))
        if (
            len(introspection_matches) >= 3
            and "EMO003" not in allowed
            and "formulaic-introspection" not in allowed
        ):
            first = introspection_matches[0]
            findings.append(
                _finding_from_span(
                    text,
                    "EMO003",
                    "formulaic-introspection",
                    "medium",
                    first.start(),
                    first.end(),
                    "Repeated vague self-interpretation explains feeling without changing action; "
                    "keep only the instance that adds contradiction, choice, or consequence.",
                )
            )

        chapter_openings = _chapter_opening_spans(masked)
        scenic_resets = [
            (start, end)
            for start, end in chapter_openings
            if len(_scene_opening_cues(masked[start:end])) >= 3
        ]
        if (
            len(chapter_openings) >= 3
            and len(scenic_resets) * 5 >= len(chapter_openings) * 3
            and "RESET001" not in allowed
            and "chapter-scenic-reset" not in allowed
        ):
            start, end = scenic_resets[0]
            findings.append(
                _finding_from_span(
                    text,
                    "RESET001",
                    "chapter-scenic-reset",
                    "medium",
                    start,
                    min(end, start + 180),
                    "Most chapters restart with a fresh scenic slate; carry forward a consequence, "
                    "object, question, or relationship pressure before re-establishing atmosphere.",
                )
            )

        run_start = None
        run_count = 0
        for start, end, paragraph in paragraphs:
            if len(paragraph) <= 24:
                if run_start is None:
                    run_start = start
                run_count += 1
                if (
                    run_count == 4
                    and "PARA001" not in allowed
                    and "fragment-run" not in allowed
                ):
                    findings.append(
                        _finding_from_span(
                            text,
                            "PARA001",
                            "fragment-run",
                            "medium",
                            run_start,
                            min(end, run_start + 160),
                            "Four or more short paragraphs run together; verify that each break marks a real turn.",
                        )
                    )
            else:
                run_start = None
                run_count = 0

    findings.sort(key=lambda finding: (finding.start, finding.rule_id))
    weighted = sum(SEVERITY_WEIGHT[finding.severity] for finding in findings)
    score = min(100, round(weighted * 500 / max(word_count, 250)))
    label = "minimal"
    if score >= 60:
        label = "heavy"
    elif score >= 35:
        label = "visible"
    elif score >= 15:
        label = "light"
    confidence = "low" if word_count < 80 else "medium" if word_count < 250 else "high"
    return LintReport(
        score=score,
        label=label,
        confidence=confidence,
        style=style,
        character_count=len(text),
        word_count=word_count,
        findings=tuple(findings),
    )


def lint_file(path: str, style: str = "general", allow: set[str] | None = None) -> LintReport:
    return lint_text(Path(path).read_text(encoding="utf-8"), style=style, allow=allow)


def format_lint_report(report: LintReport, output_format: str = "markdown") -> str:
    if output_format == "json":
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"
    lines = [
        "# Writing Pattern Lint",
        "",
        f"- Score: {report.score}/100 ({report.label})",
        f"- Confidence: {report.confidence}",
        f"- Style profile: {report.style}",
        f"- Findings: {len(report.findings)}",
        f"- Disclaimer: {report.disclaimer}",
        "",
        "| Rule | Severity | Location | Evidence | Repair direction |",
        "| --- | --- | --- | --- | --- |",
    ]
    for finding in report.findings:
        evidence = finding.excerpt.replace("|", "\\|")
        message = finding.message.replace("|", "\\|")
        lines.append(
            f"| `{finding.rule_id}` | {finding.severity} | "
            f"L{finding.line}:C{finding.column} | {evidence} | {message} |"
        )
    return "\n".join(lines) + "\n"
