"""
Date: 03AUG2026
Author: 정민규 (Minkyu Jung)
SNumber: P062

Purpose: 3개 API 응답에서 필요한 필드를 추출하고
Pydantic v2로 타입과 값의 범위를 검증한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class StrictModel(BaseModel):
    """암묵적인 타입 변환과 정의하지 않은 필드를 금지하는 공통 모델."""

    model_config = ConfigDict(strict=True, extra="forbid")


class WeatherRecord(StrictModel):
    """Open-Meteo의 서울 시간대별 날씨 데이터."""

    city: Literal["Seoul"]
    timestamp: datetime
    temperature_c: float = Field(ge=-100.0, le=60.0)
    precipitation_probability: int = Field(ge=0, le=100)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    timezone: str = Field(min_length=1)


class CountryRecord(StrictModel):
    """Countries.dev의 대한민국 국가 정보."""

    name: str = Field(min_length=1)
    native_name: str = Field(min_length=1)
    alpha2_code: str = Field(min_length=2, max_length=2)
    alpha3_code: Literal["KOR"]
    capital: str = Field(min_length=1)
    region: str = Field(min_length=1)
    subregion: str = Field(min_length=1)
    population: int = Field(ge=0)
    area_km2: float = Field(gt=0)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class IpLocationRecord(StrictModel):
    """ip-api의 8.8.8.8 기반 위치 정보."""

    status: Literal["success"]
    query: str = Field(min_length=7)
    country: str = Field(min_length=1)
    country_code: str = Field(min_length=2, max_length=2)
    region_name: str = Field(min_length=1)
    city: str = Field(min_length=1)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    timezone: str = Field(min_length=1)
    isp: str = Field(min_length=1)


@dataclass(frozen=True)
class ValidatedData:
    """검증을 통과한 세 API 데이터를 하나로 묶는 클래스."""

    weather: list[WeatherRecord]
    country: CountryRecord
    ip_location: IpLocationRecord

    def row_counts(self) -> dict[str, int]:
        """데이터셋별 검증 통과 행 수를 반환한다."""

        return {
            "weather": len(self.weather),
            "country": 1,
            "ip_location": 1,
        }


class PipelineValidationError(ValueError):
    """API 응답의 구조 또는 값이 올바르지 않을 때 발생하는 예외."""


def validate_weather(payload: dict[str, Any]) -> list[WeatherRecord]:
    """Open-Meteo의 병렬 배열을 시간대별 날씨 레코드로 변환한다."""

    hourly = payload["hourly"]

    times = hourly["time"]
    temperatures = hourly["temperature_2m"]
    precipitation_probabilities = hourly["precipitation_probability"]

    # 배열 길이가 다르면 zip 과정에서 데이터가 누락될 수 있으므로 실패 처리한다.
    lengths = {
        len(times),
        len(temperatures),
        len(precipitation_probabilities),
    }

    if len(lengths) != 1 or not times:
        raise ValueError(
            "Open-Meteo 시간, 기온, 강수확률 배열 길이가 다르거나 비어 있습니다."
        )

    latitude = float(payload["latitude"])
    longitude = float(payload["longitude"])
    timezone = payload["timezone"]

    weather_records = []

    for timestamp, temperature, probability in zip(
        times,
        temperatures,
        precipitation_probabilities,
        strict=True,
    ):
        weather_records.append(
            WeatherRecord(
                city="Seoul",
                timestamp=datetime.fromisoformat(timestamp),
                temperature_c=float(temperature),
                precipitation_probability=probability,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone,
            )
        )

    return weather_records


def validate_country(payload: dict[str, Any]) -> CountryRecord:
    """Countries.dev 응답에서 필요한 필드를 추출하여 검증한다."""

    latitude, longitude = payload["latlng"]

    return CountryRecord(
        name=payload["name"],
        native_name=payload["nativeName"],
        alpha2_code=payload["alpha2Code"],
        alpha3_code=payload["alpha3Code"],
        capital=payload["capital"],
        region=payload["region"],
        subregion=payload["subregion"],
        population=payload["population"],
        area_km2=float(payload["area"]),
        latitude=float(latitude),
        longitude=float(longitude),
    )


def validate_ip_location(payload: dict[str, Any]) -> IpLocationRecord:
    """ip-api 응답에서 필요한 필드를 추출하여 검증한다."""

    return IpLocationRecord(
        status=payload["status"],
        query=payload["query"],
        country=payload["country"],
        country_code=payload["countryCode"],
        region_name=payload["regionName"],
        city=payload["city"],
        latitude=float(payload["lat"]),
        longitude=float(payload["lon"]),
        timezone=payload["timezone"],
        isp=payload["isp"],
    )


def validate_payloads(
    payloads: dict[str, dict[str, Any]],
) -> ValidatedData:
    """세 API 응답을 API별 모델로 변환하고 검증한다."""

    try:
        return ValidatedData(
            weather=validate_weather(payloads["weather"]),
            country=validate_country(payloads["country"]),
            ip_location=validate_ip_location(payloads["ip_location"]),
        )

    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        raise PipelineValidationError(
            f"Pydantic 스키마 검증 실패: {exc}"
        ) from exc