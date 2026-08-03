"""
Date: 03AUG2026
Author: Minkyu Jung
SNumber: P062

Purpose: asyncio + httpx를 활용한 다중 비동기 API 수집 및 오프라인 로드.
"""

from __future__ import annotations

import asyncio # 빠져있던 import 추가
import json
from pathlib import Path
from typing import Any, Dict, List
import httpx


class CollectionError(Exception):
    """데이터 수집 중 오류가 발생했을 때 던지는 커스텀 예외."""
    pass


# 실습에서 수집해야 하는 3개의 API 엔드포인트 (실습용 URL)
API_ENDPOINTS = [
    "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul",
    "https://countries.dev/alpha/KOR",
    "http://ip-api.com/json/8.8.8.8",
]


async def fetch_single(client: httpx.AsyncClient, url: str) -> Any:
    """단일 API 비동기 요청"""
    response = await client.get(url, timeout=10.0)
    response.raise_for_status()
    return response.json()


async def collect_data(project_dir: Path, offline: bool = False) -> List[Dict[str, Any]]:
    """설정에 따라 3개 API 동시 수집 또는 오프라인 JSON 파일 로드"""
    
    if offline:
        target_path = project_dir / "data" / "raw_data.json"
        if not target_path.exists():
            data_dir = project_dir / "data"
            json_files = list(data_dir.glob("*.json")) if data_dir.exists() else []
            if json_files:
                target_path = json_files[0]
            else:
                raise CollectionError(f"오프라인 데이터 파일을 찾을 수 없습니다: {target_path}")

        try:
            print(f"[수집] 오프라인 모드: '{target_path.name}' 읽는 중...")
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else [data]
        except Exception as exc:
            raise CollectionError(f"오프라인 데이터 로드 실패: {exc}") from exc

    else:
        print("[수집] 온라인 모드: 3개 API 동시 비동기 수집 시작...")
        try:
            async with httpx.AsyncClient() as client:
                # asyncio.gather를 이용해 3개 API 동시 요청
                tasks = [fetch_single(client, url) for url in API_ENDPOINTS]
                results = await asyncio.gather(*tasks, return_exceptions=False)
                
                # 결과 통합 (API 응답 구조에 맞게 리스트 병합)
                combined_data = []
                for res in results:
                    if isinstance(res, list):
                        combined_data.extend(res)
                    else:
                        combined_data.append(res)
                
                return combined_data

        except Exception as exc:
            raise CollectionError(f"온라인 API 동시 수집 실패: {exc}") from exc
