"""
Date: 03AUG2026
Author: Minkyu Jung
SNumber: P062

Purpose: 파이프라인 데이터 모델 정의 및 유효성 검증 로직.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


class PipelineValidationError(Exception):
    """데이터 유효성 검증 실패 시 발생하는 예외."""
    pass


@dataclass
class RecordModel:
    """단일 데이터 레코드의 구조를 정의하고 검증한다."""
    id: int
    name: str
    value: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecordModel:
        """딕셔너리 데이터를 받아 유효성을 검증하고 모델 객체로 변환한다."""
        if not isinstance(data, dict):
            raise PipelineValidationError("데이터 형식이 딕셔너리가 아닙니다.")
        
        # 필수 키 존재 여부 확인
        required_keys = {"id", "name", "value"}
        if not required_keys.issubset(data.keys()):
            missing = required_keys - set(data.keys())
            raise PipelineValidationError(f"필수 필드가 누락되었습니다: {missing}")

        # 타입 검증 및 변환
        try:
            record_id = int(data["id"])
            name = str(data["name"])
            value = float(data["value"])

            # 비즈니스 로직 유효성 검증
            if value < 0:
                raise PipelineValidationError(f"value 값은 0 이상이어야 합니다. (입력된 값: {value})")
    
        except (ValueError, TypeError) as exc:
            raise PipelineValidationError(f"데이터 타입 변환 실패: {exc}")
        else:
            # 모든 검증을 통과한 경우 실행됨.
            print(f"[성공] 데이터 유효성 검증 통과: id={record_id}, name={name}, value={value}")                    

        return cls(id=record_id, name=name, value=value) # 모델 객체 반환
