"""셔플·뽑기·리딩 결과 생성."""
from __future__ import annotations

import hashlib
import random
import secrets
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .cards import DECK, Card
from .spreads import Position, Spread, get_spread

Seed = Union[int, str, None]


def make_seed(*parts: Any) -> int:
    """문자열·숫자 조합(질문, 날짜 등)에서 재현 가능한 32비트 시드를 만든다."""
    raw = "\x1f".join(str(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:4], "big")


def _normalize_seed(seed: Seed) -> int:
    if seed is None:
        return secrets.randbits(32)
    if isinstance(seed, bool):
        raise TypeError("seed는 정수 또는 문자열이어야 합니다")
    if isinstance(seed, int):
        return seed
    text = str(seed).strip()
    if text.isdigit():
        return int(text)
    return make_seed(text)


def shuffle_deck(seed: int) -> List[Card]:
    """시드 기반 Fisher-Yates 셔플. 같은 시드는 항상 같은 순서를 만든다."""
    rng = random.Random(seed)
    deck = list(DECK)
    for i in range(len(deck) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        deck[i], deck[j] = deck[j], deck[i]
    return deck


@dataclass(frozen=True)
class DrawnCard:
    position: Position
    card: Card
    is_reversed: bool

    @property
    def orientation(self) -> str:
        return "reversed" if self.is_reversed else "upright"

    @property
    def keywords(self):
        return self.card.reversed if self.is_reversed else self.card.upright

    def to_dict(self) -> Dict[str, Any]:
        c = self.card
        return {
            "position": self.position.key,
            "position_name": self.position.name,
            "position_description": self.position.description,
            "card_id": c.id,
            "name_en": c.name_en,
            "name_ko": c.name_ko,
            "arcana": c.arcana,
            "suit": c.suit,
            "rank": c.rank,
            "reversed": self.is_reversed,
            "orientation": self.orientation,
            "keywords": list(self.keywords),
        }


@dataclass
class Reading:
    spread: Spread
    question: str
    seed: int
    allow_reversed: bool
    cards: List[DrawnCard] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spread": self.spread.key,
            "spread_name": self.spread.name,
            "question": self.question,
            "seed": self.seed,
            "allow_reversed": self.allow_reversed,
            "cards": [c.to_dict() for c in self.cards],
        }

    def to_text(self) -> str:
        lines = [f"[{self.spread.name}]"]
        if self.question:
            lines.append(f"질문: {self.question}")
        lines.append(f"시드: {self.seed}")
        lines.append("")
        for i, d in enumerate(self.cards, 1):
            mark = "역방향" if d.is_reversed else "정방향"
            lines.append(f"{i}. {d.position.name} — {d.card.name_ko} ({d.card.name_en}) [{mark}]")
            lines.append(f"   {', '.join(d.keywords)}")
        return "\n".join(lines)


def draw(
    spread: str = "three_card",
    question: str = "",
    seed: Seed = None,
    allow_reversed: bool = True,
    reversed_chance: float = 0.5,
) -> Reading:
    """스프레드에 맞춰 카드를 뽑아 Reading을 돌려준다.

    seed를 주면 같은 입력에 항상 같은 결과가 나오고, 생략하면 무작위 시드를 만들어
    결과에 기록한다(나중에 같은 리딩을 재현할 수 있다).
    """
    if not 0.0 <= reversed_chance <= 1.0:
        raise ValueError("reversed_chance는 0~1 사이여야 합니다")
    sp = get_spread(spread)
    seed_int = _normalize_seed(seed)
    deck = shuffle_deck(seed_int)
    # 뒤집힘 판정은 셔플과 별도 스트림으로 하여 카드 순서가 방향 옵션에 영향받지 않게 한다.
    flip_rng = random.Random(seed_int ^ 0x5F3759DF)

    drawn: List[DrawnCard] = []
    for position, card in zip(sp.positions, deck):
        flip = flip_rng.random()
        is_reversed = allow_reversed and flip < reversed_chance
        drawn.append(DrawnCard(position, card, is_reversed))
    return Reading(sp, question, seed_int, allow_reversed, drawn)
