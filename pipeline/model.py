"""
Date: 03AUG2026
Author: Minkyu Jung
SNumber: P062

Purpose: Pydantic v2를 이용한 데이터 스키마 및 유효성 검증 모델.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RecordModel(BaseModel):
    """단일 데이터 레코드의 구조 및 유효성 검증 모델 (Pydantic v2)."""
    id: int
    name: str
    value: float = Field(..., ge=0, description="값은 0 이상이어야 합니다.")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name 필드는 비어있을 수 없습니다.")
        return v
