"""
Date: 03AUG2026
Author: 정민규 (Minkyu Jung)
SNumber: P062

Purpose: pytest를 활용하여 API별 Pydantic 모델의
정상값, 타입 오류, 범위 오류를 검증한다.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo  # 추가

import pytest
from pydantic import ValidationError

from pipeline.model import (
    CountryRecord,
    IpLocationRecord,
    WeatherRecord,
    validate_weather,
)


def make_valid_weather(
    **changes: object,
) -> dict[str, object]:
    """정상 날씨 데이터에서 필요한 값만 변경해 반환한다."""

    weather_data: dict[str, object] = {
    "city": "Seoul",
    "timestamp": datetime(
        2026,
        8,
        3,
        9,
        0,
        tzinfo=ZoneInfo("Asia/Seoul"),
    ),
    "temperature_c": 28.5,
    "precipitation_probability": 40,
    "latitude": 37.55,
    "longitude": 127.0,
    "timezone": "Asia/Seoul",
    }

    weather_data.update(changes)

    return weather_data


def test_weather_record_valid() -> None:
    """정상 범위의 날씨 데이터는 검증을 통과해야 한다."""

    record = WeatherRecord(
        **make_valid_weather()
    )

    assert record.city == "Seoul"
    assert record.temperature_c == 28.5
    assert record.precipitation_probability == 40
    assert record.timezone == "Asia/Seoul"


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("temperature_c", 80.0),
        ("precipitation_probability", 101),
        ("latitude", -91.0),
    ],
)
def test_weather_record_rejects_out_of_range_value(
    field_name: str,
    invalid_value: object,
) -> None:
    """온도, 강수확률, 위도가 허용 범위를 벗어나면 실패해야 한다."""

    invalid_weather = make_valid_weather(
        **{field_name: invalid_value}
    )

    with pytest.raises(ValidationError):
        WeatherRecord(**invalid_weather)


def test_weather_record_rejects_invalid_type() -> None:
    """strict 모드에서는 숫자 문자열을 실수로 변환하지 않아야 한다."""

    invalid_weather = make_valid_weather(
        temperature_c="28.5"
    )

    with pytest.raises(ValidationError):
        WeatherRecord(**invalid_weather)


def test_country_record_rejects_negative_population() -> None:
    """국가 인구가 음수이면 검증에 실패해야 한다."""

    with pytest.raises(ValidationError):
        CountryRecord(
            name="Korea (Republic of)",
            native_name="대한민국",
            alpha2_code="KR",
            alpha3_code="KOR",
            capital="Seoul",
            region="Asia",
            subregion="Eastern Asia",
            population=-1,
            area_km2=100_210.0,
            latitude=37.0,
            longitude=127.5,
        )


def test_ip_location_rejects_failure_status() -> None:
    """ip-api의 실패 응답을 정상 위치 정보로 처리하지 않아야 한다."""

    with pytest.raises(ValidationError):
        IpLocationRecord(
            status="fail",
            query="8.8.8.8",
            country="United States",
            country_code="US",
            region_name="Virginia",
            city="Ashburn",
            latitude=39.03,
            longitude=-77.5,
            timezone="America/New_York",
            isp="Google LLC",
        )


def test_weather_parallel_arrays_must_have_same_length() -> None:
    """Open-Meteo의 시간·기온·강수확률 배열 길이는 같아야 한다."""

    invalid_payload = {
        "latitude": 37.55,
        "longitude": 127.0,
        "timezone": "Asia/Seoul",
        "hourly": {
            "time": [
                "2026-08-03T00:00",
                "2026-08-03T01:00",
            ],
            "temperature_2m": [
                28.0,
            ],
            "precipitation_probability": [
                10,
                20,
            ],
        },
    }

    with pytest.raises(
        ValueError,
        match="배열 길이",
    ):
        validate_weather(invalid_payload)