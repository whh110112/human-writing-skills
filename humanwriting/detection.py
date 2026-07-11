from __future__ import annotations

import re
from dataclasses import dataclass


PIPELINE_PROFILES = [
    "logic",
    "character",
    "relationship",
    "physical",
    "ai-trace",
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


def _match_reason(pattern: re.Pattern[str], text: str, label: str) -> tuple[bool, str]:
    match = pattern.search(text)
    if not match:
        return False, f"No {label} cues found in the draft."
    cue = match.group(0).strip()
    return True, f"Detected {label} cue: {cue!r}."


def detect_audit_profiles(draft: str) -> list[ProfileDecision]:
    optional = {
        "character": _match_reason(CHARACTER_PATTERN, draft, "character-action or voice"),
        "relationship": _match_reason(RELATIONSHIP_PATTERN, draft, "dialogue or relationship"),
        "physical": _match_reason(PHYSICAL_PATTERN, draft, "space, movement, appearance, or prop"),
        "numbers": _match_reason(NUMBER_PATTERN, draft, "exact-number"),
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
