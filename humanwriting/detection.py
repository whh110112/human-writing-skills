from __future__ import annotations

import re
from dataclasses import dataclass


PIPELINE_PROFILES = [
    "logic",
    "character",
    "relationship",
    "voice",
    "serial",
    "momentum",
    "physical",
    "ai-trace",
    "texture",
    "style-match",
    "numbers",
    "proofread",
]
CORE_AUTO_PROFILES = {"logic", "ai-trace", "proofread"}


@dataclass(frozen=True)
class ProfileDecision:
    profile: str
    selected: bool
    reason: str


CHARACTER_PATTERN = re.compile(
    r"[\u4e00-\u9fff]{1,4}(?:说|问|答|想|看|走|笑|哭|摇头|点头)|"
    r"\b(?:he|she|they|said|asked|replied|thought|character)\b",
    re.IGNORECASE,
)
RELATIONSHIP_PATTERN = re.compile(
    r"[“”「」『』]|(?:说|问|告诉|提到)[:：,，]|答道|董事长|总经理|掌门|师父|师兄|师姐|夫妻|丈夫|妻子|老公|老婆|"
    r"恋人|情人|出轨|秘密|敌对|盟友|上司|下属|朋友|背叛|信任|"
    r"\b(?:said|asked|told|mentioned|boss|manager|lover|spouse|husband|wife|rival|ally|secret|betray|trust)\b",
    re.IGNORECASE,
)
PHYSICAL_PATTERN = re.compile(
    r"前排|后排|左侧|右侧|座位|椅子|床|桌|门|窗|隔板|车内|房间|电梯|走廊|"
    r"站在|坐在|躺在|走到|移到|伸手|触碰|穿着|鞋|裙|外套|伤口|拿着|放下|"
    r"\b(?:front|rear|left|right|seat|chair|bed|table|door|room|corridor|moved|"
    r"reached|touched|wearing|shoes|coat|injury|carried)\b",
    re.IGNORECASE,
)
NUMBER_PATTERN = re.compile(
    r"(?:\d+(?:\.\d+)?|[零一二两三四五六七八九十百千万点]+)\s*(?:毫米|厘米|米|公里|秒|分钟|小时|次|岁|元|%|"
    r"mm|cm|km|meters?|seconds?|minutes?|hours?|times?)",
    re.IGNORECASE,
)
NARRATIVE_PATTERN = re.compile(
    r"(?:第[一二三四五六七八九十百\d]+章|上一章|前文|回想|那天|他说|她说|"
    r"走到|坐在|望着|心里|翌日|次日)|"
    r"\b(?:chapter|previously|earlier|he said|she said|walked|sat|remembered)\b",
    re.IGNORECASE,
)
DIALOGUE_MARK_PATTERN = re.compile(r"[“「『\"]")
DIALOGUE_ATTRIBUTION_PATTERN = re.compile(
    r"(?:说|问|答|道|喊|低声|笑道|反问| replied| said| asked| whispered)",
    re.IGNORECASE,
)
IMAGERY_PATTERN = re.compile(r"像|仿佛|如同|宛如|好似|犹如|\blike\b|\bas if\b", re.IGNORECASE)
DETAIL_PATTERN = re.compile(
    r"(?:[今现]年)?\d{1,3}岁|身高|体重|职业|结婚[了]?\d|任职|毕业于|"
    r"\b(?:aged?|height|weighs?|occupation|married|graduated)\b",
    re.IGNORECASE,
)
SHOW_GLOSS_PATTERN = re.compile(
    r"(?:握紧|攥紧|避开目光|垂下眼|停住脚步|手指发抖|呼吸一滞).{0,50}"
    r"(?:愤怒|紧张|害怕|犹豫|不安|羞愧|嫉妒|悲伤)",
    re.DOTALL,
)
CHAPTER_HEADING_PATTERN = re.compile(
    r"(?m)^\s*(?:#{1,6}\s*)?(?:第\s*[一二三四五六七八九十百零〇\d]+\s*[章节回卷]|"
    r"chapter\s+\d+)[^\n]*$",
    re.IGNORECASE,
)
SCENE_TIME_PATTERN = re.compile(
    r"(?:(?:凌晨|清晨|早上|上午|中午|下午|傍晚|晚上|夜里)\s*"
    r"(?:\d{1,2}|[一二三四五六七八九十两]+)\s*(?:点|时)(?:半|\d{1,2}分)?|"
    r"(?:\d{1,2}|[一二三四五六七八九十两]+)\s*点(?:半|\d{1,2}分)?|"
    r"\d{1,2}\s*时(?:\d{1,2}分)?)",
)
SCENE_PLACE_PATTERN = re.compile(
    r"[\u4e00-\u9fffA-Za-z0-9]{2,18}(?:机场|航站楼|车站|酒店|大厦|公寓|办公室|"
    r"宿舍|宫殿|广场|餐厅|咖啡馆|会所|小区|街口|路口|码头|医院|学校)",
)
SCENE_LIGHT_PATTERN = re.compile(
    r"落日|夕阳|阳光|晨光|暮色|夜色|灯光|月光|雨|雪|雾|夜风|微风|冷风",
)
SCENE_APPEARANCE_PATTERN = re.compile(
    r"身穿|穿着|外套|短裙|长裙|西装|制服|高跟鞋|平底鞋|长发|短发|妆容",
)
SCENE_FEELING_PATTERN = re.compile(
    r"莫名|说不清|无法形容|不知为何|不知道为什么|一股.{0,16}(?:感觉|情绪)|"
    r"(?:疲惫|紧张|幸福|不安|心动)中带着?",
)
FORMULAIC_INTROSPECTION_PATTERN = re.compile(
    r"不是那种.{0,45}而是|像是.{0,35}(?:又像是|却又像)|"
    r"(?:他|她|我)不知道为什么|(?:他|她|我)?莫名(?:地|其妙|就)?|"
    r"说不清(?:是什么|为什么)|无法形容(?:的|这种)",
)


def _match_reason(pattern: re.Pattern[str], text: str, label: str) -> tuple[bool, str]:
    match = pattern.search(text)
    if not match:
        return False, f"No {label} cues found in the draft."
    cue = match.group(0).strip()
    return True, f"Detected {label} cue: {cue!r}."


def _voice_reason(text: str) -> tuple[bool, str]:
    dialogue_marks = len(DIALOGUE_MARK_PATTERN.findall(text))
    attributions = len(DIALOGUE_ATTRIBUTION_PATTERN.findall(text))
    selected = dialogue_marks >= 4 and attributions >= 2
    if not selected:
        return False, "No sustained multi-turn dialogue cues found in the draft."
    return True, f"Detected sustained dialogue: {dialogue_marks} openings and {attributions} attribution cues."


def _serial_reason(text: str, context_active: bool) -> tuple[bool, str]:
    if not context_active:
        return False, "No prior chapter or continuity context was supplied."
    match = NARRATIVE_PATTERN.search(text)
    if not match:
        return False, "Context exists, but the draft has no serialized narrative cue."
    return True, f"Prior context supplied with serialized narrative cue: {match.group(0)!r}."


def _longest_short_paragraph_run(text: str) -> int:
    longest = current = 0
    for paragraph in (part.strip() for part in re.split(r"\n\s*\n", text)):
        if paragraph and len(paragraph) <= 24:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _texture_reason(text: str) -> tuple[bool, str]:
    imagery = len(IMAGERY_PATTERN.findall(text))
    detail = len(DETAIL_PATTERN.findall(text))
    short_run = _longest_short_paragraph_run(text)
    show_gloss = bool(SHOW_GLOSS_PATTERN.search(text))
    opening_stack = _has_scene_opening_stack(text)
    introspection = len(FORMULAIC_INTROSPECTION_PATTERN.findall(text))
    narrative = bool(NARRATIVE_PATTERN.search(text) or CHARACTER_PATTERN.search(text))
    selected = narrative and (
        imagery >= 5
        or detail >= 3
        or short_run >= 4
        or show_gloss
        or opening_stack
        or introspection >= 3
    )
    if not selected:
        return False, (
            "No dense imagery, detail inventory, fragment run, cinematic opening stack, "
            "formulaic introspection, or show-then-gloss cluster found."
        )
    return True, (
        "Detected prose-texture cues: "
        f"imagery={imagery}, detail={detail}, short-paragraph-run={short_run}, "
        f"show-then-gloss={'yes' if show_gloss else 'no'}, "
        f"opening-stack={'yes' if opening_stack else 'no'}, introspection={introspection}."
    )


def _scene_opening_cues(fragment: str) -> int:
    patterns = (
        SCENE_TIME_PATTERN,
        SCENE_PLACE_PATTERN,
        SCENE_LIGHT_PATTERN,
        SCENE_APPEARANCE_PATTERN,
        SCENE_FEELING_PATTERN,
    )
    return sum(bool(pattern.search(fragment)) for pattern in patterns)


def _has_scene_opening_stack(text: str) -> bool:
    openings = [text[:700]]
    openings.extend(text[match.end() : match.end() + 700] for match in CHAPTER_HEADING_PATTERN.finditer(text))
    return any(_scene_opening_cues(opening) >= 4 for opening in openings)


def _momentum_reason(text: str) -> tuple[bool, str]:
    headings = len(CHAPTER_HEADING_PATTERN.findall(text))
    continuation_marks = len(re.findall(r"待续|未完待续|下回|下一章|to be continued", text, re.IGNORECASE))
    selected = headings >= 2 or continuation_marks >= 2
    if not selected:
        return False, "No multi-chapter or repeated continuation structure found in the draft."
    return True, (
        "Detected serial momentum structure: "
        f"chapter-headings={headings}, continuation-marks={continuation_marks}."
    )


def detect_audit_profiles(
    draft: str,
    reference_active: bool = False,
    context_active: bool = False,
) -> list[ProfileDecision]:
    optional = {
        "character": _match_reason(CHARACTER_PATTERN, draft, "character-action or voice"),
        "relationship": _match_reason(RELATIONSHIP_PATTERN, draft, "dialogue or relationship"),
        "voice": _voice_reason(draft),
        "serial": _serial_reason(draft, context_active),
        "momentum": _momentum_reason(draft),
        "physical": _match_reason(PHYSICAL_PATTERN, draft, "space, movement, appearance, or prop"),
        "texture": _texture_reason(draft),
        "numbers": _match_reason(NUMBER_PATTERN, draft, "exact-number"),
        "style-match": (
            reference_active,
            "Explicit reference material or style direction was supplied."
            if reference_active
            else "No explicit reference material or style direction was supplied.",
        ),
    }
    decisions: list[ProfileDecision] = []
    for profile in PIPELINE_PROFILES:
        if profile in CORE_AUTO_PROFILES:
            decisions.append(
                ProfileDecision(
                    profile=profile,
                    selected=True,
                    reason="Core pipeline stage retained for every draft.",
                )
            )
        else:
            selected, reason = optional[profile]
            decisions.append(ProfileDecision(profile, selected, reason))
    return decisions
