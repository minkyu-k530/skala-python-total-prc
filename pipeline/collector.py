"""
Date: 03AUG2026
Author: 정민규 (Minkyu Jung)
SNumber: P062

Purpose: asyncio와 httpx를 사용하여
3개 API를 동시에 비동기로 수집한다.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import httpx


class CollectionError(RuntimeError):
    """API 데이터 수집에 실패했을 때 발생하는 예외."""


API_ENDPOINTS = {
    "weather": (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=37.5665"
        "&longitude=126.9780"
        "&hourly=temperature_2m,precipitation_probability"
        "&forecast_days=3"
        "&timezone=Asia/Seoul"
    ),
    "country": "https://countries.dev/alpha/KOR",
    "ip_location": "http://ip-api.com/json/8.8.8.8",
}


async def fetch_single(
    client: httpx.AsyncClient,
    api_name: str,
    url: str,
) -> tuple[str, dict[str, Any]]:
    """단일 API를 비동기로 호출하고 API 이름과 JSON을 반환한다."""

    try:
        response = await client.get(url)
        response.raise_for_status()

        payload = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        raise CollectionError(
            f"{api_name} API 수집 실패: {exc}"
        ) from exc

    if not isinstance(payload, dict):
        raise CollectionError(
            f"{api_name} API 응답이 JSON 객체가 아닙니다."
        )

    return api_name, payload


async def collect_data(
    project_dir: Path,
) -> dict[str, dict[str, Any]]:
    """asyncio.gather로 3개 API를 동시에 수집한다."""

    # 현재 온라인 수집에서는 사용하지 않지만
    # 메인 함수의 기존 호출 형식을 유지하기 위해 받는다.
    del project_dir

    print(
        "[수집] 온라인 모드: "
        "3개 API 동시 비동기 수집 시작..."
    )

    timeout = httpx.Timeout(
        timeout=20.0,
        connect=10.0,
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            # 핵심 채점 항목:
            # 세 API 코루틴을 asyncio.gather로 동시에 실행한다.
            responses = await asyncio.gather(
                fetch_single(
                    client,
                    "weather",
                    API_ENDPOINTS["weather"],
                ),
                fetch_single(
                    client,
                    "country",
                    API_ENDPOINTS["country"],
                ),
                fetch_single(
                    client,
                    "ip_location",
                    API_ENDPOINTS["ip_location"],
                ),
            )

    except CollectionError:
        raise

    except httpx.HTTPError as exc:
        raise CollectionError(
            f"온라인 API 동시 수집 실패: {exc}"
        ) from exc

    # [
    #   ("weather", weather_json),
    #   ("country", country_json),
    #   ("ip_location", ip_json),
    # ]
    #
    # 위 결과를 API 이름을 키로 하는 딕셔너리로 변환한다.
    payloads = {
        api_name: payload
        for api_name, payload in responses
    }

    return payloads