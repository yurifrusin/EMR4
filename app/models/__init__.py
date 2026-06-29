from app.models.base import Base
from app.models.tenancy import Practice, PracticeLocation, User, Practitioner
from app.models.patients import Patient
from app.models.clinical import (
    Encounter, ClinicalDiagnosis, Prescription,
    Allergy, Immunisation, PatientHistory, ConsentForm, ClinicalImage,
)
from app.models.care_plans import CarePlan
from app.models.appointments import (
    Appointment, AppointmentType, PractitionerSchedule, ScheduleOverride,
)
from app.models.results import (
    TestRequest, Result, ResultItem, Referral, Reminder, ScannedDocument,
)
from app.models.billing import MbsClaim, Invoice, MbsDirectory, SnomedDirectory
from app.models.diary import DiaryTemplate, DiaryColumn, DiaryBreak, Room, DiaryRoster
from app.models.messaging import InternalMessage, SmsLog
from app.models.kiosk import CheckinEvent, PatientQrToken, CallLog
from app.models.rag import CommunityEncounter, RagFeedback, IhiRecord, MhrUpload
from app.models.ai_audit import AccessAiAuditLog

__all__ = [
    "Base",
    "Practice", "PracticeLocation", "User", "Practitioner",
    "Patient",
    "Encounter", "ClinicalDiagnosis", "Prescription",
    "Allergy", "Immunisation", "PatientHistory", "ConsentForm", "ClinicalImage",
    "CarePlan",
    "Appointment", "AppointmentType", "PractitionerSchedule", "ScheduleOverride",
    "TestRequest", "Result", "ResultItem", "Referral", "Reminder", "ScannedDocument",
    "MbsClaim", "Invoice", "MbsDirectory", "SnomedDirectory",
    "DiaryTemplate", "DiaryColumn", "DiaryBreak", "Room", "DiaryRoster",
    "InternalMessage", "SmsLog",
    "CheckinEvent", "PatientQrToken", "CallLog",
    "CommunityEncounter", "RagFeedback", "IhiRecord", "MhrUpload",
    "AccessAiAuditLog",
]
