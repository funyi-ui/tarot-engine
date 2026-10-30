import json
from collections import Counter

import pytest

from tarot_engine import DECK, SPREADS, draw, find_card, get_spread, make_seed, shuffle_deck
from tarot_engine.cli import main


def test_deck_has_78_unique_cards():
    assert len(DECK) == 78
    assert len({c.id for c in DECK}) == 78
    assert len({c.name_en for c in DECK}) == 78
    assert len({c.name_ko for c in DECK}) == 78
    assert [c.id for c in DECK] == list(range(78))


def test_deck_structure():
    assert sum(c.arcana == "major" for c in DECK) == 22
    suits = Counter(c.suit for c in DECK if c.arcana == "minor")
    assert suits == {"wands": 14, "cups": 14, "swords": 14, "pentacles": 14}
    for c in DECK:
        assert c.upright and c.reversed


def test_find_card():
    assert find_card("0").name_en == "The Fool"
    assert find_card("the fool").id == 0
    assert find_card("바보").id == 0
    assert find_card("Ace of Wands").id == 22
    assert find_card("펜타클 왕").id == 77
    with pytest.raises(KeyError):
        find_card("없는 카드")


def test_same_seed_same_reading():
    a = draw("celtic_cross", question="Q", seed=42)
    b = draw("celtic_cross", question="Q", seed=42)
    assert a.to_dict() == b.to_dict()


def test_different_seed_differs():
    assert draw("celtic_cross", seed=1).to_dict() != draw("celtic_cross", seed=2).to_dict()


def test_string_seed_is_deterministic():
    assert draw(seed="오늘의 운세").seed == draw(seed="오늘의 운세").seed == make_seed("오늘의 운세")
    assert draw(seed="42").seed == 42


def test_random_seed_is_recorded_and_replayable():
    first = draw("three_card")
    replay = draw("three_card", seed=first.seed)
    assert first.to_dict() == replay.to_dict()


@pytest.mark.parametrize("key,size", [("one_card", 1), ("three_card", 3), ("celtic_cross", 10)])
def test_spread_sizes_and_no_duplicates(key, size):
    reading = draw(key, seed=7)
    assert len(reading.cards) == size == get_spread(key).size
    assert len({d.card.id for d in reading.cards}) == size


def test_spread_aliases():
    assert get_spread("3").key == "three_card"
    assert get_spread("celtic").key == "celtic_cross"
    with pytest.raises(KeyError):
        get_spread("unknown")


def test_no_reversed_option():
    for seed in range(50):
        assert not any(d.is_reversed for d in draw("celtic_cross", seed=seed, allow_reversed=False).cards)


def test_reversed_chance_extremes():
    assert all(d.is_reversed for d in draw("celtic_cross", seed=3, reversed_chance=1.0).cards)
    assert not any(d.is_reversed for d in draw("celtic_cross", seed=3, reversed_chance=0.0).cards)
    with pytest.raises(ValueError):
        draw(reversed_chance=1.5)


def test_orientation_does_not_change_card_order():
    a = [d.card.id for d in draw("celtic_cross", seed=11, allow_reversed=True).cards]
    b = [d.card.id for d in draw("celtic_cross", seed=11, allow_reversed=False).cards]
    assert a == b


def test_shuffle_is_a_permutation():
    deck = shuffle_deck(123)
    assert sorted(c.id for c in deck) == list(range(78))


def test_to_dict_is_json_serializable():
    data = draw("three_card", question="질문", seed=5).to_dict()
    restored = json.loads(json.dumps(data, ensure_ascii=False))
    assert restored["spread"] == "three_card"
    assert len(restored["cards"]) == 3
    assert restored["cards"][0]["orientation"] in {"upright", "reversed"}


def test_keywords_follow_orientation():
    for d in draw("celtic_cross", seed=9).cards:
        expected = d.card.reversed if d.is_reversed else d.card.upright
        assert tuple(d.to_dict()["keywords"]) == expected


def test_cli_draw_json(capsys):
    assert main(["draw", "--spread", "one_card", "--seed", "42", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["seed"] == 42 and len(data["cards"]) == 1


def test_cli_draw_text_and_errors(capsys):
    assert main(["draw", "-s", "three_card", "--seed", "1", "-q", "테스트"]) == 0
    out = capsys.readouterr().out
    assert "과거" in out and "테스트" in out
    assert main(["draw", "--spread", "nope"]) == 1
    assert main(["card", "없는 카드"]) == 1


def test_cli_listing(capsys):
    assert main(["cards", "--arcana", "major"]) == 0
    assert len(capsys.readouterr().out.strip().splitlines()) == 22
    assert main(["spreads"]) == 0
    assert len(capsys.readouterr().out.strip().splitlines()) == len(SPREADS)
