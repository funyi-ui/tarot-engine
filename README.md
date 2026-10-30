# tarot-engine

78장 타로 카드 엔진입니다. 외부 의존성 없이 파이썬만으로 동작합니다.

- 메이저 22장 + 마이너 56장(완드·컵·검·펜타클) 전체 데이터, 정방향·역방향 키워드
- 스프레드: 원카드, 3카드(과거·현재·미래), 켈틱 크로스(10장)
- 시드 기반 셔플: 같은 시드면 항상 같은 결과, 시드를 생략하면 무작위 시드를 만들어 결과에 기록
- 결과를 텍스트 또는 JSON으로 출력 (홈페이지 연동용)

## 설치

```bash
git clone https://github.com/<funyi-ui명>/tarot-engine.git
cd tarot-engine
pip install -e .            # 실행 명령(tarot-engine)까지 설치
pip install -e ".[dev]"     # 테스트 도구 포함
```

## 명령줄 사용

```bash
python -m tarot_engine draw -s three_card -q "이직을 해도 될까?"
python -m tarot_engine draw -s celtic_cross --seed 42 --json
python -m tarot_engine draw -s one_card --no-reversed
python -m tarot_engine cards --arcana major
python -m tarot_engine card 바보
python -m tarot_engine spreads
```

## 파이썬에서 사용

```python
from tarot_engine import draw, make_seed

reading = draw("three_card", question="이직을 해도 될까?", seed=make_seed("홍길동", "2026-10-30"))
print(reading.to_text())
data = reading.to_dict()   # JSON으로 바로 직렬화 가능
```

`draw()` 주요 옵션

| 옵션 | 설명 |
|---|---|
| `spread` | `one_card`, `three_card`, `celtic_cross` (별칭 `1`, `3`, `celtic`) |
| `question` | 질문 문자열(결과에 그대로 포함) |
| `seed` | 정수 또는 문자열. 숫자로만 된 문자열은 숫자로 취급. 생략하면 무작위 |
| `allow_reversed` | `False`면 역방향 없이 정방향만 |
| `reversed_chance` | 역방향이 나올 확률 (기본 0.5) |

같은 시드는 셔플 순서와 역방향 판정이 모두 같습니다. 역방향 옵션을 바꿔도 카드 순서는 바뀌지 않습니다.

## 홈페이지 연동

엔진은 JSON을 돌려주므로 서버에서 API로 감싸 홈페이지가 호출하는 방식이 가장 간단합니다. FastAPI 예시:

```python
from fastapi import FastAPI
from tarot_engine import draw

app = FastAPI()

@app.get("/api/tarot")
def tarot(spread: str = "three_card", question: str = "", seed: str | None = None):
    return draw(spread, question, seed).to_dict()
```

## 테스트

```bash
pytest
```

## 구조

```
tarot_engine/
  cards.py     # 78장 카드 데이터
  spreads.py   # 스프레드 정의
  engine.py    # 셔플·뽑기·Reading
  cli.py       # 명령줄
tests/
```

카드 의미는 라이더-웨이트 계열의 일반적인 키워드를 요약한 것입니다. `cards.py`에서 자유롭게 고쳐 쓸 수 있습니다.
