"""Compatibility facade for diary-domain schedule explanation contracts."""

from app.services.diary.schedule_explanations import (
    DIARY_SCHEDULE_COPY_CATALOG,
    DIARY_SCHEDULE_REASON_ALIASES,
    DiaryScheduleCopy,
    DiaryScheduleExplanation,
    DiaryScheduleExplanationEvidence,
    DiaryScheduleExplanationReason,
    explain_schedule,
    get_schedule_copy,
    parse_schedule_explanation_reason,
)

__all__ = [
    "DIARY_SCHEDULE_COPY_CATALOG",
    "DIARY_SCHEDULE_REASON_ALIASES",
    "DiaryScheduleCopy",
    "DiaryScheduleExplanation",
    "DiaryScheduleExplanationEvidence",
    "DiaryScheduleExplanationReason",
    "explain_schedule",
    "get_schedule_copy",
    "parse_schedule_explanation_reason",
]
