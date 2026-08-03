"""
Date: 03AUG2026
Author: 정민규 (Minkyu Jung)
SNumber: P062

Purpose: Pydantic 검증을 통과한 데이터를 CSV와 Parquet으로 저장하고
두 형식의 쓰기·읽기 시간과 파일 크기를 비교한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import pandas as pd

from pipeline.model import ValidatedData


@dataclass(frozen=True)
class BenchmarkResult:
    """한 데이터셋의 CSV·Parquet 성능 측정 결과."""

    dataset: str
    rows: int
    csv_write_seconds: float
    parquet_write_seconds: float
    csv_read_seconds: float
    parquet_read_seconds: float
    csv_size_kb: float
    parquet_size_kb: float


def records_to_dataframe(records: list[object]) -> pd.DataFrame:
    """Pydantic 모델 목록을 Pandas DataFrame으로 변환한다."""

    return pd.DataFrame(
        [
            record.model_dump(mode="json")
            for record in records
        ]
    )


def measure_and_save(
    dataframe: pd.DataFrame,
    dataset_name: str,
    output_dir: Path,
) -> BenchmarkResult:
    """한 데이터셋을 CSV와 Parquet으로 저장하고 성능을 측정한다."""

    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"{dataset_name}.csv"
    parquet_path = output_dir / f"{dataset_name}.parquet"

    # CSV 쓰기 시간을 측정한다.
    start_time = perf_counter()
    dataframe.to_csv(csv_path, index=False)
    csv_write_seconds = perf_counter() - start_time

    # Parquet 쓰기 시간을 측정한다.
    start_time = perf_counter()
    dataframe.to_parquet(parquet_path, index=False)
    parquet_write_seconds = perf_counter() - start_time

    # 저장된 CSV를 다시 읽고 시간을 측정한다.
    start_time = perf_counter()
    csv_loaded = pd.read_csv(csv_path)
    csv_read_seconds = perf_counter() - start_time

    # 저장된 Parquet을 다시 읽고 시간을 측정한다.
    start_time = perf_counter()
    parquet_loaded = pd.read_parquet(parquet_path)
    parquet_read_seconds = perf_counter() - start_time

    # 두 파일을 다시 읽은 결과의 행과 열 개수가 원본과 같은지 확인한다.
    if csv_loaded.shape != dataframe.shape:
        raise RuntimeError(
            f"{dataset_name} CSV의 행·열 개수가 원본과 다릅니다."
        )

    if parquet_loaded.shape != dataframe.shape:
        raise RuntimeError(
            f"{dataset_name} Parquet의 행·열 개수가 원본과 다릅니다."
        )

    return BenchmarkResult(
        dataset=dataset_name,
        rows=len(dataframe),
        csv_write_seconds=csv_write_seconds,
        parquet_write_seconds=parquet_write_seconds,
        csv_read_seconds=csv_read_seconds,
        parquet_read_seconds=parquet_read_seconds,
        csv_size_kb=csv_path.stat().st_size / 1024,
        parquet_size_kb=parquet_path.stat().st_size / 1024,
    )


def print_benchmark(result: BenchmarkResult) -> None:
    """CSV와 Parquet 측정 결과를 실행 화면에 출력한다."""

    print()
    print("=" * 65)
    print(f"[{result.dataset} 저장 성능 비교]")
    print(f"처리 행 수: {result.rows:,}행")
    print("-" * 65)

    print("[CSV]")
    print(f"쓰기 시간: {result.csv_write_seconds:.6f}초")
    print(f"읽기 시간: {result.csv_read_seconds:.6f}초")
    print(f"파일 크기: {result.csv_size_kb:.2f}KB")

    print()

    print("[Parquet]")
    print(f"쓰기 시간: {result.parquet_write_seconds:.6f}초")
    print(f"읽기 시간: {result.parquet_read_seconds:.6f}초")
    print(f"파일 크기: {result.parquet_size_kb:.2f}KB")
    print("=" * 65)


def save_validated_data(
    validated_data: ValidatedData,
    output_dir: Path,
) -> list[BenchmarkResult]:
    """검증된 날씨·국가·IP 데이터를 각각 CSV와 Parquet으로 저장한다."""

    dataframes = {
        "weather": records_to_dataframe(validated_data.weather),
        "country": records_to_dataframe([validated_data.country]),
        "ip_location": records_to_dataframe(
            [validated_data.ip_location]
        ),
    }

    benchmark_results = []

    for dataset_name, dataframe in dataframes.items():
        result = measure_and_save(
            dataframe=dataframe,
            dataset_name=dataset_name,
            output_dir=output_dir,
        )

        benchmark_results.append(result)
        print_benchmark(result)

    return benchmark_results