"""
Date: 03AUG2026
Author: 정민규 (Minkyu Jung)
SNumber: P062

Purpose: pytest를 활용한 Pydantic 데이터 모델 유효성 검증 단위 테스트.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pipeline.model import RecordModel


def test_record_model_valid() -> None:
    """정상적인 데이터가 주어졌을 때 Pydantic 모델이 올바르게 생성되는지 테스트"""
    valid_data = {
        "id": 1,
        "name": "Test Item",
        "value": 25.5
    }
    record = RecordModel.model_validate(valid_data)
    
    assert record.id == 1
    assert record.name == "Test Item"
    assert record.value == 25.5


def test_record_model_invalid_value_range() -> None:
    """value 값이 0보다 작을 때(음수) ValidationError가 발생하는지 테스트"""
    invalid_data = {
        "id": 2,
        "name": "Negative Item",
        "value": -5.0  # ge == 0 조건 위반
    }
    
    with pytest.raises(ValidationError):
        RecordModel.model_validate(invalid_data)


def test_record_model_invalid_type() -> None:
    """필수 필드의 타입이 잘못되었거나 누락되었을 때 ValidationError가 발생하는지 테스트"""
    # id에 정수로 변환될 수 없는 문자열 전달
    invalid_data = {
        "id": "not-an-integer",
        "name": "Type Error Item",
        "value": 10.0
    }
    
    with pytest.raises(ValidationError):
        RecordModel.model_validate(invalid_data)


def test_record_model_empty_name() -> None:
    """name 필드가 빈 문자열이거나 공백일 때 커스텀 검증에 걸리는지 테스트"""
    invalid_data = {
        "id": 3,
        "name": "   ",  # 공백만 있는 경우
        "value": 15.0
    }
    
    with pytest.raises(ValidationError):
        RecordModel.model_validate(invalid_data)
