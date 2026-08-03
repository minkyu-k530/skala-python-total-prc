"""
Date: 03AUG2026
Author: 정민규 (Minkyu Jung)
SNumber: P062

Purpose: 3개 API 비동기 수집, Pydantic 검증,
CSV·Parquet 저장 및 성능 비교를 실행하는 메인 진입점.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from pipeline.collector import CollectionError, collect_data
from pipeline.model import (
    PipelineValidationError,
    validate_payloads,
)
from pipeline.storage import save_validated_data


def parse_args() -> argparse.Namespace:
    """프로그램 실행 옵션을 정의한다."""

    parser = argparse.ArgumentParser(
        description="Day 1 데이터 수집 미니 파이프라인"
    )

    parser.add_argument(
        "--offline",
        action="store_true",
        help="API 대신 data/raw에 저장된 JSON을 사용합니다.",
    )

    return parser.parse_args()


def save_raw_payloads(
    payloads: dict[str, dict[str, Any]],
    raw_dir: Path,
) -> None:
    """API에서 수집한 원본 JSON을 data/raw 폴더에 저장한다."""

    raw_dir.mkdir(parents=True, exist_ok=True)

    for api_name, payload in payloads.items():
        file_path = raw_dir / f"{api_name}.json"

        file_path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        print(f"[원본 저장] {file_path}")


def load_raw_payloads(
    raw_dir: Path,
) -> dict[str, dict[str, Any]]:
    """오프라인 실행을 위해 저장된 원본 JSON 세 개를 읽는다."""

    payloads: dict[str, dict[str, Any]] = {}

    for api_name in (
        "weather",
        "country",
        "ip_location",
    ):
        file_path = raw_dir / f"{api_name}.json"

        if not file_path.exists():
            raise CollectionError(
                f"오프라인 파일을 찾을 수 없습니다: {file_path}"
            )

        payload = json.loads(
            file_path.read_text(encoding="utf-8")
        )

        if not isinstance(payload, dict):
            raise CollectionError(
                f"{file_path}의 최상위 데이터가 JSON 객체가 아닙니다."
            )

        payloads[api_name] = payload

    return payloads


async def main() -> None:
    """수집, 검증, 저장 단계를 순서대로 실행한다."""

    args = parse_args()

    project_dir = Path(__file__).resolve().parent
    raw_dir = project_dir / "data" / "raw"
    processed_dir = project_dir / "data" / "processed"

    print("=" * 65)
    print("[Day 1 데이터 수집 미니 파이프라인 시작]")
    print(
        f"실행 모드: {'오프라인' if args.offline else '온라인'}"
    )
    print("=" * 65)

    try:
        # 1. 온라인 또는 오프라인 방식으로 원본 데이터를 확보한다.
        if args.offline:
            payloads = load_raw_payloads(raw_dir)
            print("[수집 완료] 저장된 원본 JSON 3개를 읽었습니다.")

        else:
            payloads = await collect_data(project_dir)
            print("[수집 완료] 3개 API 응답을 수집했습니다.")

            # 온라인으로 받은 원본 데이터는 재현을 위해 JSON으로 저장한다.
            save_raw_payloads(payloads, raw_dir)

        # 2. API별 Pydantic 모델로 타입과 범위를 검증한다.
        validated_data = validate_payloads(payloads)

        print()
        print("[Pydantic 검증 완료]")
        print(
            f"날씨 데이터: {len(validated_data.weather)}행"
        )
        print("국가 데이터: 1행")
        print("IP 위치 데이터: 1행")

        # 3. 검증을 통과한 데이터만 CSV와 Parquet으로 저장한다.
        benchmark_results = save_validated_data(
            validated_data=validated_data,
            output_dir=processed_dir,
        )

        print()
        print(
            f"[전체 완료] {len(benchmark_results)}개 데이터셋을 "
            "CSV와 Parquet으로 저장했습니다."
        )

    except CollectionError as exc:
        print(f"[수집 실패] {exc}")

    except PipelineValidationError as exc:
        print(f"[검증 실패] {exc}")

    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[처리 실패] {exc}")


if __name__ == "__main__":
    asyncio.run(main())