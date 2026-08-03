"""
Date: 03AUG2026
Author: 정민규 (Minkyu Jung)
SNumber: P062

Purpose: 비동기 데이터 파이프라인 메인 진입점 (오케스트레이터).
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from pydantic import ValidationError

from pipeline.collector import collect_data, CollectionError
from pipeline.model import RecordModel
from pipeline.storage import save_and_benchmark


async def main() -> None:
    """파이프라인 전체 실행 흐름 제어"""
    parser = argparse.ArgumentParser(description="Day 1 비동기 파이프라인 및 벤치마크 도구")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="온라인 API 수집 대신 로컬 JSON 파일을 오프라인으로 읽습니다.",
    )
    args = parser.parse_args()

    project_dir = Path(__file__).parent
    output_dir = project_dir / "output"

    print("=" * 50)
    print("[Day 1 파이프라인 실행 시작]") 
    print(f" - 실행 모드: {'오프라인 (Local JSON)' if args.offline else '온라인 (Async API)'}")
    print("=" * 50)

    try:
        # 1. 데이터 수집 (비동기)
        raw_data_list = await collect_data(project_dir, offline=args.offline)
        print(f"[수집 완료] 총 {len(raw_data_list)}건의 원본 데이터를 수집했습니다.")

        # 2. 스키마 및 범위 검증 (Pydantic v2)
        validated_records: list[RecordModel] = []
        for idx, item in enumerate(raw_data_list):
            try:
                # Pydantic 모델 파싱 및 검증
                record = RecordModel.model_validate(item)
                validated_records.append(record)
            except ValidationError as val_err:
                print(f"[검증 경고] {idx}번째 레코드 검증 실패 (제외됨): {val_err}")

        print(f"[검증 완료] 유효성 검증 통과 데이터: {len(validated_records)}건")

        if not validated_records:
            print("[오류] 저장할 수 있는 유효한 데이터가 존재하지 않습니다.")
            return

        # 3. 저장 및 성능 비교 벤치마크 실행
        save_and_benchmark(validated_records, output_dir)
        print("\n✨ 모든 파이프라인 작업이 성공적으로 완료되었습니다!")

    except CollectionError as col_err:
        print(f"\n[수집 오류 발생] {col_err}")
    except Exception as exc:
        print(f"\n[예기치 못한 오류 발생] {exc}")


if __name__ == "__main__":
    asyncio.run(main())
