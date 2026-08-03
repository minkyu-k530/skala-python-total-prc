"""
Date: 03AUG2026
Author: 정민규 (Minkyu Jung)
SNumber: P062

Purpose: 검증된 데이터를 CSV 및 Parquet 형식으로 저장하고 읽기/쓰기 성능을 비교하는 모듈.
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import List
import pyarrow as pa
import pyarrow.parquet as pq

from pipeline.model import RecordModel


def save_and_benchmark(data: List[RecordModel], output_dir: Path) -> None:
    """데이터를 CSV와 Parquet으로 저장하고 각각의 읽기/쓰기 성능을 측정하여 비교한다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / "output.csv"
    parquet_path = output_dir / "output.parquet"
    
    # 모델 객체 리스트를 순수 딕셔너리 리스트로 변환
    dict_data = [item.model_dump() for item in data]
    if not dict_data:
        print("[경고] 저장할 데이터가 없습니다.")
        return

    fields = list(dict_data[0].keys())

    # ==========================================
    # 1. CSV 형식 성능 측정 (쓰기 / 읽기)
    # ==========================================
    start_time = time.perf_counter()
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(dict_data)
    csv_write_duration = time.perf_counter() - start_time

    start_time = time.perf_counter()
    csv_read_data = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_read_data.append(row)
    csv_read_duration = time.perf_counter() - start_time

    # ==========================================
    # 2. Parquet 형식 성능 측정 (쓰기 / 읽기)
    # ==========================================
    table_data = {field: [item[field] for item in dict_data] for field in fields}
    pa_table = pa.Table.from_pydict(table_data)

    start_time = time.perf_counter()
    pq.write_table(pa_table, parquet_path)
    parquet_write_duration = time.perf_counter() - start_time

    start_time = time.perf_counter()
    parquet_table = pq.read_table(parquet_path)
    parquet_read_data = parquet_table.to_pylist()
    parquet_read_duration = time.perf_counter() - start_time

    # ==========================================
    # 3. 결과 리포트 출력
    # ==========================================
    print("\n" + "="*45)
    print("📊 [성능 비교 벤치마크 결과]") # pipeline과 동일하게 이모지 사용 [Feat(pipeline/pipeline.py): refer == pipeline's 81 Line Comment]
    print("="*45)
    print(f"처리된 레코드 수: {len(data)}건\n")
    
    print(f"[CSV]")
    print(f" - 쓰기 시간: {csv_write_duration:.6f} 초")
    print(f" - 읽기 시간: {csv_read_duration:.6f} 초")
    print(f" - 파일 크기: {csv_path.stat().st_size / 1024:.2f} KB")
    
    print(f"\n[Parquet]")
    print(f" - 쓰기 시간: {parquet_write_duration:.6f} 초")
    print(f" - 읽기 시간: {parquet_read_duration:.6f} 초")
    print(f" - 파일 크기: {parquet_path.stat().st_size / 1024:.2f} KB")
    print("="*45)
