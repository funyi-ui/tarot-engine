"""스프레드(카드 배열) 정의."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Position:
    key: str
    name: str
    description: str


@dataclass(frozen=True)
class Spread:
    key: str
    name: str
    positions: Tuple[Position, ...]

    @property
    def size(self) -> int:
        return len(self.positions)


SPREADS: Dict[str, Spread] = {
    "one_card": Spread(
        "one_card",
        "원카드",
        (Position("answer", "답", "질문에 대한 핵심 메시지"),),
    ),
    "three_card": Spread(
        "three_card",
        "3카드 (과거·현재·미래)",
        (
            Position("past", "과거", "현재 상황에 영향을 준 배경"),
            Position("present", "현재", "지금의 상황과 에너지"),
            Position("future", "미래", "이 흐름이 이어질 때의 전개"),
        ),
    ),
    "celtic_cross": Spread(
        "celtic_cross",
        "켈틱 크로스",
        (
            Position("present", "현재 상황", "질문의 중심이 되는 지금의 상태"),
            Position("challenge", "도전·장애", "가로질러 놓이는 문제나 영향"),
            Position("foundation", "근원", "상황의 밑바탕, 무의식적 기반"),
            Position("past", "과거", "방금 지나간 영향"),
            Position("conscious", "의식·목표", "스스로 바라보는 목표나 가능한 최선"),
            Position("near_future", "가까운 미래", "곧 다가올 전개"),
            Position("self", "나의 태도", "질문자의 입장과 자세"),
            Position("environment", "주변 환경", "주변 사람과 외부 영향"),
            Position("hopes_fears", "희망과 두려움", "기대와 걱정이 얽힌 지점"),
            Position("outcome", "최종 결과", "현재 흐름이 이어질 때의 결과"),
        ),
    ),
}

_ALIASES = {
    "1": "one_card",
    "one": "one_card",
    "3": "three_card",
    "three": "three_card",
    "celtic": "celtic_cross",
}


def get_spread(key: str) -> Spread:
    """스프레드 키(또는 별칭)로 스프레드를 가져온다. 없으면 KeyError."""
    k = _ALIASES.get(key, key)
    if k not in SPREADS:
        raise KeyError(f"알 수 없는 스프레드입니다: {key!r} (사용 가능: {', '.join(SPREADS)})")
    return SPREADS[k]
