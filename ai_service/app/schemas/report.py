from datetime import date

from pydantic import BaseModel, Field, field_validator


class ReportRequest(BaseModel):
    meeting_date: date
    participants: str = Field(min_length=1, max_length=2000)

    @field_validator("participants")
    @classmethod
    def normalize_participants(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("participants must not be blank")
        return value


class ReportResponse(BaseModel):
    report_text: str
