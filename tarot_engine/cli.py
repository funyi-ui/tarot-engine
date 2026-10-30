"""명령줄 인터페이스: python -m tarot_engine ..."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .cards import DECK, find_card
from .engine import draw
from .spreads import SPREADS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tarot-engine", description="타로 카드 엔진")
    sub = parser.add_subparsers(dest="command", required=True)

    p_draw = sub.add_parser("draw", help="카드를 뽑아 리딩을 만든다")
    p_draw.add_argument("--spread", "-s", default="three_card", help="one_card | three_card | celtic_cross")
    p_draw.add_argument("--question", "-q", default="", help="질문(선택)")
    p_draw.add_argument("--seed", default=None, help="재현용 시드(숫자 또는 문자열)")
    p_draw.add_argument("--no-reversed", action="store_true", help="역방향 없이 정방향만 사용")
    p_draw.add_argument("--json", action="store_true", help="JSON으로 출력")

    p_cards = sub.add_parser("cards", help="카드 목록을 본다")
    p_cards.add_argument("--arcana", choices=["major", "minor"])
    p_cards.add_argument("--suit", choices=["wands", "cups", "swords", "pentacles"])

    p_card = sub.add_parser("card", help="카드 한 장의 의미를 본다 (id/영문명/한글명)")
    p_card.add_argument("name")

    sub.add_parser("spreads", help="사용 가능한 스프레드 목록")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        if args.command == "draw":
            reading = draw(
                spread=args.spread,
                question=args.question,
                seed=args.seed,
                allow_reversed=not args.no_reversed,
            )
            if args.json:
                print(json.dumps(reading.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(reading.to_text())

        elif args.command == "cards":
            for c in DECK:
                if args.arcana and c.arcana != args.arcana:
                    continue
                if args.suit and c.suit != args.suit:
                    continue
                print(f"{c.id:>2}  {c.name_ko} ({c.name_en})")

        elif args.command == "card":
            c = find_card(args.name)
            print(f"{c.name_ko} ({c.name_en})")
            print(f"정방향: {', '.join(c.upright)}")
            print(f"역방향: {', '.join(c.reversed)}")

        elif args.command == "spreads":
            for sp in SPREADS.values():
                print(f"{sp.key:<13} {sp.name} ({sp.size}장)")

    except (KeyError, ValueError) as exc:
        print(f"오류: {exc.args[0] if exc.args else exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
