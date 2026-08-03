# 데이터 수집 미니 파이프라인 [Day 1] 종합 실습

3개의 공개 API를 비동기로 동시에 수집하고, Pydantic v2로 타입과 값의 범위를 검증한 뒤 CSV와 Parquet 형식으로 저장하고 성능을 비교하는 실습 프로젝트입니다.

## 작성자 정보

| 구분 | 내용 |
|---|---|
| Date | 03AUG2026 |
| Author | 정민규 (Minkyu Jung) |
| SNumber | P062 |
| Campus | 판교 |
| Class | 2반 |

## 주요 기능

- `asyncio`와 `httpx`를 이용한 3개 API 동시 수집
- `asyncio.gather()` 기반 비동기 파이프라인
- API 원본 JSON 저장
- Pydantic v2 기반 타입 및 범위 검증
- 검증 통과 데이터를 CSV와 Parquet으로 저장
- CSV와 Parquet의 읽기·쓰기 시간 측정
- 저장 후 파일 재읽기를 통한 행·열 개수 검증
- pytest 기반 정상값·범위 오류·타입 오류 테스트
- ruff 기반 코드 스타일 검사
- 저장된 JSON을 이용한 오프라인 실행 지원

## 사용 API

### Open-Meteo

서울의 3일 시간대별 기온과 강수확률을 수집합니다.

```text
https://api.open-meteo.com/v1/forecast
```

수집 항목:

- 시간
- 2m 기준 기온
- 강수확률
- 위도와 경도
- 시간대

### Countries.dev

대한민국의 국가 정보를 수집합니다.

```text
https://countries.dev/alpha/KOR
```

수집 항목:

- 국가명
- 국가 코드
- 수도
- 지역
- 인구
- 면적
- 위도와 경도

### ip-api

Google Public DNS인 `8.8.8.8`의 IP 기반 위치 정보를 수집합니다.

```text
http://ip-api.com/json/8.8.8.8
```

수집 항목:

- 조회 상태
- IP 주소
- 국가
- 지역
- 도시
- 위도와 경도
- 시간대
- ISP

## 프로젝트 구조

```text
total_practice/
├── .gitignore
├── README.md
├── requirements.txt
├── 판교_2반_정민규.py
├── test_pipeline.py
├── pipeline/
│   ├── __init__.py
│   ├── collector.py
│   ├── model.py
│   └── storage.py
└── data/
    ├── raw/
    │   └── .gitkeep
    └── processed/
        └── .gitkeep
```

각 파일의 역할은 다음과 같습니다.

| 파일 | 역할 |
|---|---|
| `pipeline/collector.py` | 3개 API 비동기 동시 수집 |
| `pipeline/model.py` | API별 Pydantic 모델 및 데이터 검증 |
| `pipeline/storage.py` | CSV·Parquet 저장 및 성능 측정 |
| `판교_2반_정민규.py` | 전체 파이프라인 실행 |
| `test_pipeline.py` | Pydantic 검증 테스트 |
| `requirements.txt` | 프로젝트 패키지 및 버전 관리 |
| `.gitignore` | 가상환경, 캐시, 생성 데이터 제외 |

## 환경 구성

### 1. 저장소 복제

HTTPS를 사용하는 경우:

```bash
git clone https://github.com/minkyu-k530/skala-python-total-prc.git
cd skala-python-total-prc
```

SSH를 사용하는 경우:

```bash
git clone git@github.com:minkyu-k530/skala-python-total-prc.git
cd skala-python-total-prc
```

### 2. 가상환경 생성

```bash
python3 -m venv .venv
```

### 3. 가상환경 활성화

macOS 또는 Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

가상환경이 정상적으로 활성화되면 터미널 앞에 다음 표시가 나타납니다.

```text
(.venv)
```

### 4. 패키지 설치

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

설치되는 주요 패키지는 다음과 같습니다.

```text
httpx
pydantic
pandas
pyarrow
numpy
pytest
ruff
```

## 온라인 파이프라인 실행

프로젝트 최상위 폴더에서 다음 명령을 실행합니다.

```bash
python "판교_2반_정민규.py"
```

정상 실행 시 다음 작업이 순서대로 수행됩니다.

1. 3개 API 비동기 동시 수집
2. API 원본 JSON 저장
3. Pydantic v2 타입·범위 검증
4. 검증된 데이터 CSV 저장
5. 검증된 데이터 Parquet 저장
6. 두 형식의 읽기·쓰기 시간 측정
7. 저장 파일 재읽기 검증

주요 실행 결과는 다음과 같습니다.

```text
[수집 완료] 3개 API 응답을 수집했습니다.

[Pydantic 검증 완료]
날씨 데이터: 72행
국가 데이터: 1행
IP 위치 데이터: 1행

[전체 완료] 3개 데이터셋을 CSV와 Parquet으로 저장했습니다.
```

## 오프라인 실행

온라인 실행을 한 번 완료하면 API 원본 JSON이 `data/raw`에 저장됩니다.

저장된 데이터를 이용해 API 호출 없이 다시 실행할 수 있습니다.

```bash
python "판교_2반_정민규.py" --offline
```

오프라인 실행에 필요한 파일은 다음과 같습니다.

```text
data/raw/weather.json
data/raw/country.json
data/raw/ip_location.json
```

## 데이터 저장 위치

### 원본 데이터

API에서 수집한 원본 JSON은 다음 위치에 저장됩니다.

```text
data/raw/
├── weather.json
├── country.json
└── ip_location.json
```

### 검증 및 가공 데이터

Pydantic 검증을 통과한 데이터는 다음 위치에 저장됩니다.

```text
data/processed/
├── weather.csv
├── weather.parquet
├── country.csv
├── country.parquet
├── ip_location.csv
└── ip_location.parquet
```

실행 결과로 생성되는 JSON, CSV, Parquet 파일은 `.gitignore`에 의해 Git 커밋에서 제외됩니다.

빈 폴더 구조를 Git에 유지하기 위해 `.gitkeep` 파일만 커밋합니다.

## Pydantic 검증 항목

### 날씨 데이터

- 기온: -100°C 이상, 60°C 이하
- 강수확률: 0% 이상, 100% 이하
- 위도: -90 이상, 90 이하
- 경도: -180 이상, 180 이하
- Open-Meteo 병렬 배열 길이 일치 여부

### 국가 데이터

- 국가명과 수도의 빈 문자열 여부
- 국가 코드 길이
- 대한민국 국가 코드 `KOR`
- 인구가 0 이상인지 확인
- 면적이 0보다 큰지 확인
- 위도와 경도 범위

### IP 위치 데이터

- API 응답 상태가 `success`인지 확인
- 국가 코드 길이
- 도시와 국가 정보 존재 여부
- 위도와 경도 범위
- ISP 정보 존재 여부

## 테스트 실행

다음 명령으로 Pydantic 모델 테스트를 실행합니다.

```bash
python -m pytest -v
```

현재 테스트 항목은 다음과 같습니다.

- 정상 날씨 데이터 검증
- 온도 범위 오류
- 강수확률 범위 오류
- 위도 범위 오류
- 숫자 필드 타입 오류
- 국가 인구 범위 오류
- IP API 실패 상태
- 날씨 병렬 배열 길이 불일치

정상 결과:

```text
collected 8 items
8 passed
```

## 코드 스타일 검사

다음 명령으로 ruff 검사를 실행합니다.

```bash
ruff check .
```

또는 현재 가상환경의 Python을 통해 실행할 수 있습니다.

```bash
python -m ruff check .
```

정상 결과:

```text
All checks passed!
```

자동 수정 가능한 스타일 문제를 수정하려면 다음 명령을 사용할 수 있습니다.

```bash
ruff check . --fix
```

자동 수정 후에는 다시 검사합니다.

```bash
ruff check .
```

## CSV와 Parquet 비교

프로그램은 각 데이터셋을 CSV와 Parquet으로 저장하고 다음 항목을 비교합니다.

- CSV 쓰기 시간
- CSV 읽기 시간
- CSV 파일 크기
- Parquet 쓰기 시간
- Parquet 읽기 시간
- Parquet 파일 크기

현재 API 데이터는 최대 72행으로 매우 작기 때문에 CSV가 더 빠르고 작은 결과가 나타날 수 있습니다.

Parquet은 스키마와 메타데이터를 포함하므로 작은 데이터에서는 고정 비용이 상대적으로 크게 나타납니다. 데이터가 10만 행 또는 100만 행 수준으로 증가하면 Parquet의 열 기반 저장과 압축 장점이 더 명확해질 수 있습니다.

## Git 상태 확인

커밋 전에는 다음 명령으로 변경 내용을 확인합니다.

```bash
git status
```

`.venv`, API 원본 JSON, CSV, Parquet 파일은 커밋 목록에 나타나지 않아야 합니다.

Git 이력은 다음 명령으로 확인할 수 있습니다.

```bash
git log --oneline --graph --all
```

## 실행 확인 순서

제출 전 다음 순서로 확인합니다.

```bash
source .venv/bin/activate
python "판교_2반_정민규.py"
python -m pytest -v
ruff check .
git status
git log --oneline --graph --all
```

확인해야 하는 결과:

```text
API 3개 수집 성공
날씨 데이터 72행 검증
국가 데이터 1행 검증
IP 위치 데이터 1행 검증
CSV와 Parquet 저장 성공
pytest 8건 통과
ruff 오류 없음
Git 커밋 이력 존재
```

## 제출 파일

제출 ZIP 파일명:

```text
판교_2반_정민규_day1종합실습.zip
```

ZIP 파일에는 다음 항목을 포함합니다.

- 프로젝트 전체 코드
- `requirements.txt`
- `README.md`
- 테스트 코드
- 실행 결과 PDF

다음 항목은 ZIP에서 제외합니다.

- `.venv`
- `__pycache__`
- `.pytest_cache`
- `.ruff_cache`
- 대용량 성능 비교 임시 파일

## 실행 환경

본 프로젝트는 다음 환경에서 실행 및 검증하였습니다.

```text
Python 3.14.6
pytest 9.1.1
ruff 0.16.1
Pydantic v2
```

## 최종 검증 결과

```text
비동기 API 수집: 성공
Pydantic 검증: 성공
CSV 저장 및 읽기: 성공
Parquet 저장 및 읽기: 성공
pytest: 8 passed
ruff: All checks passed
Git 및 GitHub 연동: 완료
```