"""phase_0_baseline

Revision ID: d4787e8e3629
Revises: 
Create Date: 2026-06-13 22:25:59.005106

"""
from collections import Counter
from contextlib import contextmanager
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = 'd4787e8e3629'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


EMPTY_BOOTSTRAP_MARKER_TYPE = "emr4_phase0_empty_bootstrap_marker"
LEGACY_CORE_TABLES = {
    "patients",
    "encounters",
    "mbs_claims",
    "clinical_diagnoses",
    "prescriptions",
}
LEGACY_DIRECTORY_TABLES = {"mbs_directory", "snomed_directory"}


def _create_legacy_core_tables() -> None:
    """Create the exact pre-Phase-0 tables expected by this baseline."""
    op.create_table(
        "patients",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("medicare_number", sa.String(length=20), nullable=True),
        sa.Column("ihi_number", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "encounters",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=True),
        sa.Column("google_doc_id", sa.String(length=255), nullable=False),
        sa.Column(
            "consultation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("is_finalized", sa.Boolean(), nullable=True),
        sa.Column("consultation_type", sa.String(length=255), nullable=True),
        sa.Column("raw_document_text", sa.Text(), nullable=True),
        sa.Column(
            "document_embedding",
            pgvector.sqlalchemy.vector.VECTOR(dim=768),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mbs_claims",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("encounter_id", sa.UUID(), nullable=True),
        sa.Column("item_number", sa.String(length=10), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["encounter_id"], ["encounters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "clinical_diagnoses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=True),
        sa.Column("encounter_id", sa.UUID(), nullable=True),
        sa.Column("term", sa.String(length=255), nullable=False),
        sa.Column("snomed_ct_au_code", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["encounter_id"], ["encounters.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "prescriptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("patient_id", sa.UUID(), nullable=True),
        sa.Column("encounter_id", sa.UUID(), nullable=True),
        sa.Column("drug_name", sa.String(length=255), nullable=False),
        sa.Column("dosage_text", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["encounter_id"], ["encounters.id"]),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def _create_missing_directory_tables(existing_tables: set[str]) -> None:
    if "mbs_directory" not in existing_tables:
        op.create_table(
            "mbs_directory",
            sa.Column("item_number", sa.String(length=10), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("fee", sa.String(length=20), nullable=True),
            sa.PrimaryKeyConstraint("item_number"),
        )
    if "snomed_directory" not in existing_tables:
        op.create_table(
            "snomed_directory",
            sa.Column("concept_id", sa.String(length=50), nullable=False),
            sa.Column("term", sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint("concept_id"),
        )


OWNED_ENUM_TYPES = {
    "appointmentstatus", "bookingchannel", "calltype", "careplanstatus",
    "careplantype", "checkinmethod", "claimstatus", "claimtype", "documenttype",
    "encounterstatus", "gptier", "historycategory", "ihisource", "invoicestatus",
    "messagepriority", "mhrdocumenttype", "referralstatus", "remindertype",
    "requeststatus", "requesttype", "resultflag", "resultsource", "resultstatus",
    "smsdirection", "smsstatus", "smstype", "templatetype", "triagestatus", "userrole",
}
PHASE0_NEW_TABLES = {
    "allergies", "appointment_types", "appointments", "call_log", "care_plans",
    "checkin_events", "clinical_images", "community_encounters", "consent_forms",
    "ihi_records", "immunisations", "internal_messages", "invoices", "mhr_uploads",
    "patient_history", "patient_qr_tokens", "practice_locations", "practices",
    "practitioner_schedules", "practitioners", "rag_feedback", "referrals",
    "reminders", "result_items", "results", "scanned_documents",
    "schedule_overrides", "sms_log", "test_requests", "users",
}

# Exact recognised pre-Phase-0 column shape: name, PostgreSQL type, nullable,
# server default. No implicit data conversion or backfill is supported.
LEGACY_COLUMNS = {
    "patients": (
        ("id", "uuid", False, None),
        ("first_name", "character varying(100)", False, None),
        ("last_name", "character varying(100)", False, None),
        ("date_of_birth", "date", False, None),
        ("medicare_number", "character varying(20)", True, None),
        ("ihi_number", "character varying(20)", True, None),
    ),
    "encounters": (
        ("id", "uuid", False, None),
        ("patient_id", "uuid", True, None),
        ("google_doc_id", "character varying(255)", False, None),
        ("consultation_date", "timestamp with time zone", True, "CURRENT_TIMESTAMP"),
        ("is_finalized", "boolean", True, None),
        ("consultation_type", "character varying(255)", True, None),
        ("raw_document_text", "text", True, None),
        ("document_embedding", "vector(768)", True, None),
    ),
    "mbs_claims": (
        ("id", "uuid", False, None),
        ("encounter_id", "uuid", True, None),
        ("item_number", "character varying(10)", False, None),
        ("description", "text", True, None),
        ("status", "character varying(20)", True, None),
    ),
    "clinical_diagnoses": (
        ("id", "uuid", False, None),
        ("patient_id", "uuid", True, None),
        ("encounter_id", "uuid", True, None),
        ("term", "character varying(255)", False, None),
        ("snomed_ct_au_code", "character varying(50)", True, None),
    ),
    "prescriptions": (
        ("id", "uuid", False, None),
        ("patient_id", "uuid", True, None),
        ("encounter_id", "uuid", True, None),
        ("drug_name", "character varying(255)", False, None),
        ("dosage_text", "text", True, None),
        ("is_active", "boolean", True, None),
    ),
    "mbs_directory": (
        ("item_number", "character varying(10)", False, None),
        ("description", "text", False, None),
        ("fee", "character varying(20)", True, None),
    ),
    "snomed_directory": (
        ("concept_id", "character varying(50)", False, None),
        ("term", "character varying(255)", False, None),
    ),
}
LEGACY_FOREIGN_KEYS = {
    "patients": set(),
    "encounters": {("patient_id", "patients", "id")},
    "mbs_claims": {("encounter_id", "encounters", "id")},
    "clinical_diagnoses": {
        ("patient_id", "patients", "id"), ("encounter_id", "encounters", "id"),
    },
    "prescriptions": {
        ("patient_id", "patients", "id"), ("encounter_id", "encounters", "id"),
    },
    "mbs_directory": set(),
    "snomed_directory": set(),
}


# Fixed post-upgrade contract derived statically from migration d2c66aadecb0e35f...
# and reviewed proposal c86dc5d3d7235fab...; never captured from a live database.
# Columns: name, declared type, nullable, server default. Physical order is irrelevant.
POST_UPGRADE_COLUMNS = {
    'allergies': (
        ('id', 'uuid', False, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('reaction', 'text', True, None),
        ('recorded_date', 'date', True, None),
        ('severity', 'character varying(50)', True, None),
        ('snomed_code', 'character varying(50)', True, None),
        ('substance', 'character varying(255)', False, None),
    ),
    'appointment_types': (
        ('color_hex', 'character varying(7)', True, None),
        ('default_duration', 'integer', True, None),
        ('id', 'uuid', False, None),
        ('is_bookable_online', 'boolean', True, None),
        ('name', 'character varying(100)', False, None),
        ('practice_id', 'uuid', False, None),
    ),
    'appointments': (
        ('appointment_type_id', 'uuid', True, None),
        ('booked_by', 'uuid', True, None),
        ('booked_via', 'bookingchannel', True, None),
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('duration_minutes', 'integer', True, None),
        ('id', 'uuid', False, None),
        ('location_id', 'uuid', True, None),
        ('notes', 'character varying(1000)', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('practitioner_id', 'uuid', False, None),
        ('queue_position', 'integer', True, None),
        ('reason', 'character varying(500)', True, None),
        ('start_time', 'timestamp with time zone', False, None),
        ('status', 'appointmentstatus', True, None),
        ('waiting_room', 'character varying(50)', True, None),
    ),
    'call_log': (
        ('answered_by', 'uuid', True, None),
        ('call_time', 'timestamp with time zone', True, 'now()'),
        ('call_type', 'calltype', False, None),
        ('caller_number', 'character varying(20)', True, None),
        ('duration_seconds', 'integer', True, None),
        ('id', 'uuid', False, None),
        ('notes', 'character varying(1000)', True, None),
        ('patient_id', 'uuid', True, None),
        ('practice_id', 'uuid', False, None),
    ),
    'care_plans': (
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('encounter_id', 'uuid', True, None),
        ('id', 'uuid', False, None),
        ('mbs_item', 'character varying(20)', True, None),
        ('patient_id', 'uuid', False, None),
        ('plan_data', 'jsonb', True, None),
        ('plan_type', 'careplantype', False, None),
        ('practice_id', 'uuid', False, None),
        ('review_date', 'date', True, None),
        ('status', 'careplanstatus', True, None),
        ('valid_until', 'date', True, None),
    ),
    'checkin_events': (
        ('appointment_id', 'uuid', True, None),
        ('checkin_method', 'checkinmethod', False, None),
        ('checkin_time', 'timestamp with time zone', True, 'now()'),
        ('id', 'uuid', False, None),
        ('kiosk_id', 'character varying(50)', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('waiting_room_assigned', 'character varying(50)', True, None),
    ),
    'clinical_diagnoses': (
        ('encounter_id', 'uuid', True, None),
        ('id', 'uuid', False, None),
        ('is_active', 'boolean', True, None),
        ('onset_date', 'date', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('resolved_date', 'date', True, None),
        ('severity', 'character varying(50)', True, None),
        ('snomed_ct_au_code', 'character varying(50)', True, None),
        ('term', 'character varying(255)', False, None),
    ),
    'clinical_images': (
        ('body_site', 'character varying(100)', True, None),
        ('caption', 'text', True, None),
        ('captured_at', 'timestamp with time zone', True, 'now()'),
        ('encounter_id', 'uuid', True, None),
        ('id', 'uuid', False, None),
        ('image_url', 'character varying(500)', False, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
    ),
    'community_encounters': (
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('deidentified_text', 'text', False, None),
        ('encounter_embedding', 'vector(768)', True, None),
        ('gp_tier', 'gptier', True, None),
        ('id', 'uuid', False, None),
        ('mbs_item', 'character varying(20)', True, None),
        ('practice_asgc_ra_code', 'character varying(10)', True, None),
        ('practice_latitude', 'double precision', True, None),
        ('practice_longitude', 'double precision', True, None),
        ('practice_specialty_tags', 'jsonb', True, None),
        ('snomed_codes', 'jsonb', True, None),
        ('source_practice_id', 'uuid', True, None),
    ),
    'consent_forms': (
        ('document_path', 'character varying(500)', True, None),
        ('encounter_id', 'uuid', True, None),
        ('form_type', 'character varying(100)', False, None),
        ('id', 'uuid', False, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('signature_data', 'text', True, None),
        ('signed_at', 'timestamp with time zone', True, None),
    ),
    'encounters': (
        ('appointment_id', 'uuid', True, None),
        ('consultation_date', 'timestamp with time zone', True, 'CURRENT_TIMESTAMP'),
        ('consultation_type', 'character varying(255)', True, None),
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('document_embedding', 'vector(768)', True, None),
        ('google_doc_id', 'character varying(255)', True, None),
        ('id', 'uuid', False, None),
        ('is_finalized', 'boolean', True, None),
        ('is_shared_to_hive', 'boolean', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('practitioner_id', 'uuid', True, None),
        ('raw_document_text', 'text', True, None),
        ('status', 'encounterstatus', True, None),
        ('template_type', 'templatetype', True, None),
        ('updated_at', 'timestamp with time zone', True, 'now()'),
    ),
    'ihi_records': (
        ('id', 'uuid', False, None),
        ('ihi_number', 'character varying(20)', False, None),
        ('ihi_status', 'character varying(50)', True, None),
        ('patient_id', 'uuid', False, None),
        ('source', 'ihisource', True, None),
        ('verified_at', 'timestamp with time zone', True, None),
    ),
    'immunisations': (
        ('air_notification_sent', 'boolean', True, None),
        ('batch_number', 'character varying(50)', True, None),
        ('date_given', 'date', True, None),
        ('dose_number', 'character varying(10)', True, None),
        ('id', 'uuid', False, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('route', 'character varying(50)', True, None),
        ('site', 'character varying(50)', True, None),
        ('vaccine_name', 'character varying(255)', False, None),
    ),
    'internal_messages': (
        ('appointment_id', 'uuid', True, None),
        ('body', 'text', False, None),
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('id', 'uuid', False, None),
        ('is_read', 'boolean', True, None),
        ('patient_id', 'uuid', True, None),
        ('practice_id', 'uuid', False, None),
        ('priority', 'messagepriority', True, None),
        ('read_at', 'timestamp with time zone', True, None),
        ('recipient_id', 'uuid', True, None),
        ('recipient_role', 'character varying(50)', True, None),
        ('sender_id', 'uuid', False, None),
        ('subject', 'character varying(255)', True, None),
    ),
    'invoices': (
        ('encounter_id', 'uuid', True, None),
        ('id', 'uuid', False, None),
        ('issued_at', 'timestamp with time zone', True, None),
        ('paid_amount', 'numeric(10,2)', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('status', 'invoicestatus', True, None),
        ('total_amount', 'numeric(10,2)', True, None),
    ),
    'mbs_claims': (
        ('amount', 'numeric(10,2)', True, None),
        ('claim_status', 'claimstatus', True, None),
        ('claim_type', 'claimtype', True, None),
        ('description', 'text', True, None),
        ('encounter_id', 'uuid', True, None),
        ('gateway_claim_id', 'character varying(100)', True, None),
        ('id', 'uuid', False, None),
        ('item_number', 'character varying(10)', False, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('practitioner_id', 'uuid', True, None),
        ('response_data', 'jsonb', True, None),
        ('submitted_at', 'timestamp with time zone', True, None),
    ),
    'mbs_directory': (
        ('description', 'text', False, None),
        ('fee', 'character varying(20)', True, None),
        ('item_number', 'character varying(10)', False, None),
    ),
    'mhr_uploads': (
        ('document_type', 'mhrdocumenttype', False, None),
        ('encounter_id', 'uuid', True, None),
        ('id', 'uuid', False, None),
        ('mhr_document_id', 'character varying(100)', True, None),
        ('patient_id', 'uuid', False, None),
        ('upload_status', 'character varying(50)', True, None),
        ('uploaded_at', 'timestamp with time zone', True, None),
    ),
    'patient_history': (
        ('category', 'historycategory', False, None),
        ('date_recorded', 'date', True, None),
        ('description', 'text', False, None),
        ('id', 'uuid', False, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
    ),
    'patient_qr_tokens': (
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('expires_at', 'timestamp with time zone', False, None),
        ('id', 'uuid', False, None),
        ('patient_id', 'uuid', False, None),
        ('token_hash', 'character varying(255)', False, None),
    ),
    'patients': (
        ('address_line1', 'character varying(255)', True, None),
        ('address_postcode', 'character varying(10)', True, None),
        ('address_state', 'character varying(10)', True, None),
        ('address_suburb', 'character varying(100)', True, None),
        ('concession_type', 'character varying(50)', True, None),
        ('consent_facial_recognition', 'boolean', True, None),
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('date_of_birth', 'date', False, None),
        ('dva_number', 'character varying(20)', True, None),
        ('email', 'character varying(255)', True, None),
        ('emergency_contact_name', 'character varying(200)', True, None),
        ('emergency_contact_phone', 'character varying(20)', True, None),
        ('emergency_contact_relationship', 'character varying(50)', True, None),
        ('face_embedding_id', 'character varying(255)', True, None),
        ('first_name', 'character varying(100)', False, None),
        ('gender_identity', 'character varying(50)', True, None),
        ('id', 'uuid', False, None),
        ('ihi_number', 'character varying(20)', True, None),
        ('indigenous_status', 'character varying(50)', True, None),
        ('last_name', 'character varying(100)', False, None),
        ('medicare_number', 'character varying(20)', True, None),
        ('phone_home', 'character varying(20)', True, None),
        ('phone_mobile', 'character varying(20)', True, None),
        ('practice_id', 'uuid', False, None),
        ('preferred_language', 'character varying(50)', True, None),
        ('sex', 'character varying(10)', True, None),
        ('sms_consent', 'boolean', True, None),
        ('sms_consent_date', 'timestamp with time zone', True, None),
        ('updated_at', 'timestamp with time zone', True, 'now()'),
    ),
    'practice_locations': (
        ('address_line1', 'character varying(255)', True, None),
        ('address_postcode', 'character varying(10)', True, None),
        ('address_state', 'character varying(10)', True, None),
        ('address_suburb', 'character varying(100)', True, None),
        ('id', 'uuid', False, None),
        ('is_active', 'boolean', True, None),
        ('name', 'character varying(255)', False, None),
        ('phone', 'character varying(20)', True, None),
        ('practice_id', 'uuid', False, None),
        ('waiting_rooms', 'jsonb', True, None),
    ),
    'practices': (
        ('abn', 'character varying(20)', True, None),
        ('address_line1', 'character varying(255)', True, None),
        ('address_line2', 'character varying(255)', True, None),
        ('address_postcode', 'character varying(10)', True, None),
        ('address_state', 'character varying(10)', True, None),
        ('address_suburb', 'character varying(100)', True, None),
        ('asgc_ra_code', 'character varying(10)', True, None),
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('email', 'character varying(255)', True, None),
        ('hive_mind_opt_in', 'boolean', True, None),
        ('id', 'uuid', False, None),
        ('latitude', 'double precision', True, None),
        ('logo_url', 'character varying(500)', True, None),
        ('longitude', 'double precision', True, None),
        ('name', 'character varying(255)', False, None),
        ('phone', 'character varying(20)', True, None),
        ('practice_embedding', 'vector(768)', True, None),
        ('proda_cert_expiry', 'timestamp with time zone', True, None),
        ('proda_device_cert_path', 'character varying(500)', True, None),
        ('specialty_tags', 'jsonb', True, None),
        ('timezone', 'character varying(50)', True, None),
    ),
    'practitioner_schedules': (
        ('day_of_week', 'integer', False, None),
        ('end_time', 'time without time zone', False, None),
        ('id', 'uuid', False, None),
        ('location_id', 'uuid', True, None),
        ('practitioner_id', 'uuid', False, None),
        ('slot_duration_minutes', 'integer', True, None),
        ('start_time', 'time without time zone', False, None),
    ),
    'practitioners': (
        ('ahpra_number', 'character varying(20)', True, None),
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('default_location_id', 'uuid', True, None),
        ('first_name', 'character varying(100)', False, None),
        ('hpi_i', 'character varying(20)', True, None),
        ('id', 'uuid', False, None),
        ('is_active', 'boolean', True, None),
        ('last_name', 'character varying(100)', False, None),
        ('practice_id', 'uuid', False, None),
        ('prescriber_number', 'character varying(20)', True, None),
        ('provider_number', 'character varying(20)', True, None),
        ('specialty', 'character varying(100)', True, None),
    ),
    'prescriptions': (
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('dosage_text', 'text', True, None),
        ('drug_name', 'character varying(255)', False, None),
        ('encounter_id', 'uuid', True, None),
        ('end_date', 'date', True, None),
        ('erx_token', 'character varying(255)', True, None),
        ('frequency', 'character varying(100)', True, None),
        ('id', 'uuid', False, None),
        ('is_active', 'boolean', True, None),
        ('patient_id', 'uuid', False, None),
        ('pbs_code', 'character varying(20)', True, None),
        ('practice_id', 'uuid', False, None),
        ('prescribed_by', 'uuid', True, None),
        ('quantity', 'character varying(20)', True, None),
        ('repeats', 'character varying(10)', True, None),
        ('route', 'character varying(50)', True, None),
        ('start_date', 'date', True, None),
    ),
    'rag_feedback': (
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('encounter_id', 'uuid', True, None),
        ('id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('query_embedding', 'vector(768)', True, None),
        ('retrieved_community_ids', 'jsonb', True, None),
        ('was_accepted', 'boolean', True, None),
    ),
    'referrals': (
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('encounter_id', 'uuid', True, None),
        ('id', 'uuid', False, None),
        ('letter_document_path', 'character varying(500)', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('practitioner_id', 'uuid', True, None),
        ('reason', 'text', True, None),
        ('referral_to', 'character varying(255)', True, None),
        ('specialty', 'character varying(100)', True, None),
        ('status', 'referralstatus', True, None),
        ('urgency', 'character varying(50)', True, None),
    ),
    'reminders': (
        ('due_date', 'date', True, None),
        ('id', 'uuid', False, None),
        ('is_dismissed', 'boolean', True, None),
        ('message', 'text', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('practitioner_id', 'uuid', True, None),
        ('reminder_type', 'remindertype', False, None),
        ('triggered_by_result_id', 'uuid', True, None),
    ),
    'result_items': (
        ('flag', 'resultflag', True, None),
        ('id', 'uuid', False, None),
        ('loinc_code', 'character varying(20)', True, None),
        ('reference_range', 'character varying(100)', True, None),
        ('result_id', 'uuid', False, None),
        ('test_name', 'character varying(255)', False, None),
        ('units', 'character varying(50)', True, None),
        ('value', 'character varying(100)', True, None),
    ),
    'results': (
        ('ai_summary', 'text', True, None),
        ('display_pdf_url', 'character varying(500)', True, None),
        ('id', 'uuid', False, None),
        ('is_abnormal', 'boolean', True, None),
        ('lab_name', 'character varying(255)', True, None),
        ('parsed_data', 'jsonb', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('raw_message', 'text', True, None),
        ('received_at', 'timestamp with time zone', True, 'now()'),
        ('report_date', 'date', True, None),
        ('result_source', 'resultsource', False, None),
        ('reviewed_at', 'timestamp with time zone', True, None),
        ('reviewed_by', 'uuid', True, None),
        ('specimen_date', 'date', True, None),
        ('status', 'resultstatus', True, None),
        ('test_request_id', 'uuid', True, None),
    ),
    'scanned_documents': (
        ('document_type', 'documenttype', False, None),
        ('file_url', 'character varying(500)', False, None),
        ('id', 'uuid', False, None),
        ('notes', 'text', True, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('scanned_at', 'timestamp with time zone', True, 'now()'),
        ('triage_status', 'triagestatus', True, None),
        ('triaged_to', 'uuid', True, None),
    ),
    'schedule_overrides': (
        ('date', 'date', False, None),
        ('id', 'uuid', False, None),
        ('is_unavailable', 'boolean', True, None),
        ('override_end', 'time without time zone', True, None),
        ('override_start', 'time without time zone', True, None),
        ('practitioner_id', 'uuid', False, None),
        ('reason', 'character varying(255)', True, None),
    ),
    'sms_log': (
        ('clicksend_message_id', 'character varying(100)', True, None),
        ('direction', 'smsdirection', False, None),
        ('id', 'uuid', False, None),
        ('message_body', 'text', False, None),
        ('patient_id', 'uuid', True, None),
        ('phone_number', 'character varying(20)', False, None),
        ('practice_id', 'uuid', False, None),
        ('sent_at', 'timestamp with time zone', True, 'now()'),
        ('sms_type', 'smstype', True, None),
        ('status', 'smsstatus', True, None),
    ),
    'snomed_directory': (
        ('concept_id', 'character varying(50)', False, None),
        ('term', 'character varying(255)', False, None),
    ),
    'test_requests': (
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('encounter_id', 'uuid', True, None),
        ('id', 'uuid', False, None),
        ('patient_id', 'uuid', False, None),
        ('practice_id', 'uuid', False, None),
        ('practitioner_id', 'uuid', True, None),
        ('request_text', 'text', True, None),
        ('request_type', 'requesttype', False, None),
        ('status', 'requeststatus', True, None),
        ('urgency', 'character varying(50)', True, None),
    ),
    'users': (
        ('created_at', 'timestamp with time zone', True, 'now()'),
        ('email', 'character varying(255)', False, None),
        ('id', 'uuid', False, None),
        ('is_active', 'boolean', True, None),
        ('password_hash', 'character varying(255)', False, None),
        ('practice_id', 'uuid', False, None),
        ('practitioner_id', 'uuid', True, None),
        ('role', 'userrole', False, None),
    ),
}

# Constraint names are generated; ordered keys and multiplicity are semantic.
POST_UPGRADE_CONSTRAINTS = {
    'allergies': (
        ('p', ('id',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'appointment_types': (
        ('p', ('id',), None, ()),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'appointments': (
        ('p', ('id',), None, ()),
        ('f', ('appointment_type_id',), 'appointment_types', ('id',)),
        ('f', ('booked_by',), 'users', ('id',)),
        ('f', ('location_id',), 'practice_locations', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
    ),
    'call_log': (
        ('p', ('id',), None, ()),
        ('f', ('answered_by',), 'users', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'care_plans': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'checkin_events': (
        ('p', ('id',), None, ()),
        ('f', ('appointment_id',), 'appointments', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'clinical_diagnoses': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'clinical_images': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'community_encounters': (
        ('p', ('id',), None, ()),
        ('f', ('source_practice_id',), 'practices', ('id',)),
    ),
    'consent_forms': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'encounters': (
        ('p', ('id',), None, ()),
        ('f', ('appointment_id',), 'appointments', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
    ),
    'ihi_records': (
        ('p', ('id',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
    ),
    'immunisations': (
        ('p', ('id',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'internal_messages': (
        ('p', ('id',), None, ()),
        ('f', ('appointment_id',), 'appointments', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('recipient_id',), 'users', ('id',)),
        ('f', ('sender_id',), 'users', ('id',)),
    ),
    'invoices': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'mbs_claims': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
    ),
    'mbs_directory': (
        ('p', ('item_number',), None, ()),
    ),
    'mhr_uploads': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
    ),
    'patient_history': (
        ('p', ('id',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'patient_qr_tokens': (
        ('p', ('id',), None, ()),
        ('u', ('token_hash',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
    ),
    'patients': (
        ('p', ('id',), None, ()),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'practice_locations': (
        ('p', ('id',), None, ()),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'practices': (
        ('p', ('id',), None, ()),
    ),
    'practitioner_schedules': (
        ('p', ('id',), None, ()),
        ('f', ('location_id',), 'practice_locations', ('id',)),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
    ),
    'practitioners': (
        ('p', ('id',), None, ()),
        ('f', ('default_location_id',), 'practice_locations', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'prescriptions': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('prescribed_by',), 'practitioners', ('id',)),
    ),
    'rag_feedback': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'referrals': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
    ),
    'reminders': (
        ('p', ('id',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
        ('f', ('triggered_by_result_id',), 'results', ('id',)),
    ),
    'result_items': (
        ('p', ('id',), None, ()),
        ('f', ('result_id',), 'results', ('id',)),
    ),
    'results': (
        ('p', ('id',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('reviewed_by',), 'practitioners', ('id',)),
        ('f', ('test_request_id',), 'test_requests', ('id',)),
    ),
    'scanned_documents': (
        ('p', ('id',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('triaged_to',), 'practitioners', ('id',)),
    ),
    'schedule_overrides': (
        ('p', ('id',), None, ()),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
    ),
    'sms_log': (
        ('p', ('id',), None, ()),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
    ),
    'snomed_directory': (
        ('p', ('concept_id',), None, ()),
    ),
    'test_requests': (
        ('p', ('id',), None, ()),
        ('f', ('encounter_id',), 'encounters', ('id',)),
        ('f', ('patient_id',), 'patients', ('id',)),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
    ),
    'users': (
        ('p', ('id',), None, ()),
        ('u', ('email',), None, ()),
        ('f', ('practice_id',), 'practices', ('id',)),
        ('f', ('practitioner_id',), 'practitioners', ('id',)),
    ),
}

# Names are used explicitly by reversal; preserve every standalone index.
POST_UPGRADE_INDEXES = {
    'allergies': (('ix_allergies_patient_id', ('patient_id',)),),
    'appointment_types': (('ix_appointment_types_practice_id', ('practice_id',)),),
    'appointments': (('ix_appointments_patient_id', ('patient_id',)), ('ix_appointments_practice_id', ('practice_id',)), ('ix_appointments_practitioner_id', ('practitioner_id',)), ('ix_appointments_start_time', ('start_time',))),
    'call_log': (('ix_call_log_practice_id', ('practice_id',)),),
    'care_plans': (('ix_care_plans_patient_id', ('patient_id',)), ('ix_care_plans_practice_id', ('practice_id',))),
    'checkin_events': (('ix_checkin_events_patient_id', ('patient_id',)),),
    'clinical_diagnoses': (('ix_clinical_diagnoses_patient_id', ('patient_id',)), ('ix_clinical_diagnoses_practice_id', ('practice_id',))),
    'clinical_images': (('ix_clinical_images_patient_id', ('patient_id',)),),
    'community_encounters': (),
    'consent_forms': (('ix_consent_forms_patient_id', ('patient_id',)),),
    'encounters': (('ix_encounters_patient_id', ('patient_id',)), ('ix_encounters_practice_id', ('practice_id',))),
    'ihi_records': (('ix_ihi_records_patient_id', ('patient_id',)),),
    'immunisations': (('ix_immunisations_patient_id', ('patient_id',)),),
    'internal_messages': (('ix_internal_messages_practice_id', ('practice_id',)), ('ix_internal_messages_recipient_id', ('recipient_id',))),
    'invoices': (('ix_invoices_patient_id', ('patient_id',)),),
    'mbs_claims': (('ix_mbs_claims_claim_status', ('claim_status',)), ('ix_mbs_claims_patient_id', ('patient_id',)), ('ix_mbs_claims_practice_id', ('practice_id',))),
    'mbs_directory': (),
    'mhr_uploads': (('ix_mhr_uploads_patient_id', ('patient_id',)),),
    'patient_history': (('ix_patient_history_patient_id', ('patient_id',)),),
    'patient_qr_tokens': (('ix_patient_qr_tokens_patient_id', ('patient_id',)),),
    'patients': (('ix_patients_last_name', ('last_name',)), ('ix_patients_medicare_number', ('medicare_number',)), ('ix_patients_practice_id', ('practice_id',))),
    'practice_locations': (('ix_practice_locations_practice_id', ('practice_id',)),),
    'practices': (),
    'practitioner_schedules': (('ix_practitioner_schedules_practitioner_id', ('practitioner_id',)),),
    'practitioners': (('ix_practitioners_practice_id', ('practice_id',)),),
    'prescriptions': (('ix_prescriptions_patient_id', ('patient_id',)),),
    'rag_feedback': (('ix_rag_feedback_practice_id', ('practice_id',)),),
    'referrals': (('ix_referrals_patient_id', ('patient_id',)),),
    'reminders': (('ix_reminders_patient_id', ('patient_id',)), ('ix_reminders_practice_id', ('practice_id',))),
    'result_items': (('ix_result_items_result_id', ('result_id',)),),
    'results': (('ix_results_patient_id', ('patient_id',)), ('ix_results_practice_id', ('practice_id',)), ('ix_results_status', ('status',))),
    'scanned_documents': (('ix_scanned_documents_patient_id', ('patient_id',)),),
    'schedule_overrides': (('ix_schedule_overrides_practitioner_id_date', ('practitioner_id', 'date')),),
    'sms_log': (('ix_sms_log_patient_id', ('patient_id',)), ('ix_sms_log_practice_id', ('practice_id',))),
    'snomed_directory': (),
    'test_requests': (('ix_test_requests_patient_id', ('patient_id',)),),
    'users': (('ix_users_email', ('email',)), ('ix_users_practice_id', ('practice_id',))),
}

POST_UPGRADE_ENUMS = {
    'appointmentstatus': ('Booked', 'Confirmed', 'Arrived', 'InConsult', 'Completed', 'Cancelled', 'NoShow', 'DNA'),
    'bookingchannel': ('Receptionist', 'Online', 'Phone', 'Kiosk', 'App'),
    'calltype': ('Inbound', 'Outbound', 'Telehealth', 'Missed'),
    'careplanstatus': ('Draft', 'Active', 'Review_Due', 'Completed'),
    'careplantype': ('GPCCMP', 'MHTP', 'HealthAssessment45', 'HealthAssessment75', 'ATSI_HA', 'Antenatal'),
    'checkinmethod': ('Details', 'QR', 'NFC', 'FacialRecognition'),
    'claimstatus': ('Draft', 'Submitted', 'Accepted', 'Rejected', 'Paid'),
    'claimtype': ('BulkBill', 'PatientClaim', 'DVA', 'WorkCover', 'TAC', 'ECLIPSE'),
    'documenttype': ('SpecialistLetter', 'Report', 'Correspondence', 'Other'),
    'encounterstatus': ('Draft', 'InProgress', 'Finalized', 'Amended'),
    'gptier': ('Tier1_Gold', 'Tier2', 'Tier3'),
    'historycategory': ('Medical', 'Surgical', 'Family', 'Social'),
    'ihisource': ('Manual', 'HI_Service'),
    'invoicestatus': ('Draft', 'Issued', 'Paid', 'Overdue', 'Cancelled'),
    'messagepriority': ('Normal', 'Urgent', 'Critical'),
    'mhrdocumenttype': ('SharedHealthSummary', 'EventSummary', 'DischargeSummary', 'Other'),
    'referralstatus': ('Draft', 'Sent', 'Accepted', 'Completed'),
    'remindertype': ('ResultFollowUp', 'Recall', 'ReviewAppointment', 'CarePlanReview', 'Custom'),
    'requeststatus': ('Pending', 'ResultReceived', 'Reviewed'),
    'requesttype': ('Pathology', 'Radiology', 'Specialist', 'Other'),
    'resultflag': ('Normal', 'Low', 'High', 'Critical'),
    'resultsource': ('PIT', 'HL7', 'Manual', 'Scan'),
    'resultstatus': ('New', 'Reviewed', 'ActionRequired', 'Filed'),
    'smsdirection': ('Outbound', 'Inbound'),
    'smsstatus': ('Queued', 'Sent', 'Delivered', 'Failed', 'Replied'),
    'smstype': ('AppointmentReminder', 'Confirmation', 'ResultNotification', 'Recall', 'Bulk', 'Custom'),
    'templatetype': ('SOAP', 'Procedure', 'MentalHealth', 'CDM', 'GPCCMP', 'HealthAssessment', 'Antenatal', 'WoundCare'),
    'triagestatus': ('Pending', 'Triaged', 'Reviewed'),
    'userrole': ('GP', 'Receptionist', 'Nurse', 'Admin', 'PracticeOwner'),
}


# PostgreSQL 16 catalog identities; no format_type/search-path erasure.
# namespace, type, typmod, kind, extension, extension namespace, collation namespace/name
POST_TYPE_FACTS = {
    'appointmentstatus': ('public', 'appointmentstatus', -1, 'e', None, None, None, None),
    'bookingchannel': ('public', 'bookingchannel', -1, 'e', None, None, None, None),
    'boolean': ('pg_catalog', 'bool', -1, 'b', None, None, None, None),
    'calltype': ('public', 'calltype', -1, 'e', None, None, None, None),
    'careplanstatus': ('public', 'careplanstatus', -1, 'e', None, None, None, None),
    'careplantype': ('public', 'careplantype', -1, 'e', None, None, None, None),
    'character varying(10)': ('pg_catalog', 'varchar', 14, 'b', None, None, 'pg_catalog', 'default'),
    'character varying(100)': ('pg_catalog', 'varchar', 104, 'b', None, None, 'pg_catalog', 'default'),
    'character varying(1000)': ('pg_catalog', 'varchar', 1004, 'b', None, None, 'pg_catalog', 'default'),
    'character varying(20)': ('pg_catalog', 'varchar', 24, 'b', None, None, 'pg_catalog', 'default'),
    'character varying(200)': ('pg_catalog', 'varchar', 204, 'b', None, None, 'pg_catalog', 'default'),
    'character varying(255)': ('pg_catalog', 'varchar', 259, 'b', None, None, 'pg_catalog', 'default'),
    'character varying(50)': ('pg_catalog', 'varchar', 54, 'b', None, None, 'pg_catalog', 'default'),
    'character varying(500)': ('pg_catalog', 'varchar', 504, 'b', None, None, 'pg_catalog', 'default'),
    'character varying(7)': ('pg_catalog', 'varchar', 11, 'b', None, None, 'pg_catalog', 'default'),
    'checkinmethod': ('public', 'checkinmethod', -1, 'e', None, None, None, None),
    'claimstatus': ('public', 'claimstatus', -1, 'e', None, None, None, None),
    'claimtype': ('public', 'claimtype', -1, 'e', None, None, None, None),
    'date': ('pg_catalog', 'date', -1, 'b', None, None, None, None),
    'documenttype': ('public', 'documenttype', -1, 'e', None, None, None, None),
    'double precision': ('pg_catalog', 'float8', -1, 'b', None, None, None, None),
    'encounterstatus': ('public', 'encounterstatus', -1, 'e', None, None, None, None),
    'gptier': ('public', 'gptier', -1, 'e', None, None, None, None),
    'historycategory': ('public', 'historycategory', -1, 'e', None, None, None, None),
    'ihisource': ('public', 'ihisource', -1, 'e', None, None, None, None),
    'integer': ('pg_catalog', 'int4', -1, 'b', None, None, None, None),
    'invoicestatus': ('public', 'invoicestatus', -1, 'e', None, None, None, None),
    'jsonb': ('pg_catalog', 'jsonb', -1, 'b', None, None, None, None),
    'messagepriority': ('public', 'messagepriority', -1, 'e', None, None, None, None),
    'mhrdocumenttype': ('public', 'mhrdocumenttype', -1, 'e', None, None, None, None),
    'numeric(10,2)': ('pg_catalog', 'numeric', 655366, 'b', None, None, None, None),
    'referralstatus': ('public', 'referralstatus', -1, 'e', None, None, None, None),
    'remindertype': ('public', 'remindertype', -1, 'e', None, None, None, None),
    'requeststatus': ('public', 'requeststatus', -1, 'e', None, None, None, None),
    'requesttype': ('public', 'requesttype', -1, 'e', None, None, None, None),
    'resultflag': ('public', 'resultflag', -1, 'e', None, None, None, None),
    'resultsource': ('public', 'resultsource', -1, 'e', None, None, None, None),
    'resultstatus': ('public', 'resultstatus', -1, 'e', None, None, None, None),
    'smsdirection': ('public', 'smsdirection', -1, 'e', None, None, None, None),
    'smsstatus': ('public', 'smsstatus', -1, 'e', None, None, None, None),
    'smstype': ('public', 'smstype', -1, 'e', None, None, None, None),
    'templatetype': ('public', 'templatetype', -1, 'e', None, None, None, None),
    'text': ('pg_catalog', 'text', -1, 'b', None, None, 'pg_catalog', 'default'),
    'time without time zone': ('pg_catalog', 'time', -1, 'b', None, None, None, None),
    'timestamp with time zone': ('pg_catalog', 'timestamptz', -1, 'b', None, None, None, None),
    'triagestatus': ('public', 'triagestatus', -1, 'e', None, None, None, None),
    'userrole': ('public', 'userrole', -1, 'e', None, None, None, None),
    'uuid': ('pg_catalog', 'uuid', -1, 'b', None, None, None, None),
    'vector(768)': ('public', 'vector', 768, 'b', 'vector', 'public', None, None),
}


@contextmanager
def _preservation_transaction():
    """Require transactional online PostgreSQL; undo even a late DDL refusal."""
    context = op.get_context()
    bind = op.get_bind()
    if context.as_sql or bind.dialect.name != "postgresql":
        raise RuntimeError("Phase-0 preservation checks require online PostgreSQL")
    driver_connection = bind.connection.driver_connection
    if (not bind.in_transaction()
            or bind.get_execution_options().get("isolation_level") == "AUTOCOMMIT"
            or getattr(driver_connection, "autocommit", False)):
        raise RuntimeError("Phase-0 requires an explicit non-autocommit transaction")
    if bind.execute(sa.text("SHOW transaction_isolation")).scalar_one() != "read committed":
        raise RuntimeError("Phase-0 requires READ COMMITTED to avoid stale row checks")
    with bind.begin_nested():
        # Explicit pg_temp placement prevents temporary tables shadowing public.
        op.execute("SET LOCAL search_path TO public, pg_catalog, pg_temp")
        op.execute("SET LOCAL row_security = off")
        op.execute("SET LOCAL lock_timeout = '5s'")
        # Serialise type-catalog writers before any name/OID ownership checks.
        # A privileged development role is required; insufficient permission or
        # a concurrent DDL lock timeout refuses without changing persistent data.
        # This locks catalog writes, never writes catalog rows directly.
        op.execute("LOCK TABLE pg_catalog.pg_type IN SHARE ROW EXCLUSIVE MODE")
        yield


def _public_tables() -> set[str]:
    """Reject views, foreign/partitioned tables and other unexpected relations."""
    rows = op.get_bind().execute(sa.text("""
        SELECT c.relname, c.relkind, c.relpersistence, c.relrowsecurity,
               c.relforcerowsecurity, c.relispartition,
               EXISTS (SELECT 1 FROM pg_catalog.pg_inherits i
                       WHERE i.inhrelid = c.oid OR i.inhparent = c.oid) AS inherited,
               EXISTS (SELECT 1 FROM pg_catalog.pg_trigger t
                       WHERE t.tgrelid = c.oid AND NOT t.tgisinternal) AS triggers,
               EXISTS (SELECT 1 FROM pg_catalog.pg_rewrite r
                       WHERE r.ev_class = c.oid) AS rules
        FROM pg_catalog.pg_class c
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind NOT IN ('i', 'I', 't')
    """)).mappings().all()
    tables = set()
    for row in rows:
        if (row["relkind"] != "r" or row["relpersistence"] != "p"
                or any(row[key] for key in (
                    "relrowsecurity", "relforcerowsecurity", "relispartition",
                    "inherited", "triggers", "rules",
                ))):
            raise RuntimeError("Phase-0 refuses unexpected public relation features")
        if row["relname"] != "alembic_version":
            tables.add(row["relname"])
    return tables


def _lock_tables(tables: set[str]) -> None:
    if tables:
        names = ", ".join(f'public."{name}"' for name in sorted(tables))
        op.execute(f"LOCK TABLE {names} IN ACCESS EXCLUSIVE MODE")


def _require_no_other_writer_transactions() -> None:
    # Completed type-DDL statements can release their catalog relation lock
    # before their transaction commits. Catalog write exclusion blocks new type
    # changes; this gate refuses earlier unfinished writers before taking a
    # READ COMMITTED ownership/admission snapshot. Transaction-ID locks are
    # cluster-wide: do not filter by database or omit prepared transactions.
    unfinished_writer = op.get_bind().execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_catalog.pg_locks
            WHERE locktype = 'transactionid' AND mode = 'ExclusiveLock'
              AND granted
              AND (pid IS NULL OR pid <> pg_catalog.pg_backend_pid())
        )
    """)).scalar_one()
    if unfinished_writer:
        raise RuntimeError("Phase-0 refuses other active writer transactions during schema preservation")


def _require_empty(tables: set[str], direction: str) -> None:
    for name in sorted(tables):
        if op.get_bind().execute(
            sa.text(f'SELECT EXISTS (SELECT 1 FROM public."{name}")')
        ).scalar_one():
            raise RuntimeError(
                f"Phase-0 {direction} refuses populated table {name}; "
                "no conversion or deletion is authorised"
            )


def _validate_legacy_shape(tables: set[str]) -> None:
    inspector = sa.inspect(op.get_bind())
    for name in sorted(tables):
        columns = op.get_bind().execute(sa.text("""
            SELECT a.attname, pg_catalog.format_type(a.atttypid, a.atttypmod),
                   NOT a.attnotnull, pg_catalog.pg_get_expr(d.adbin, d.adrelid),
                   a.attidentity, a.attgenerated
            FROM pg_catalog.pg_attribute a
            LEFT JOIN pg_catalog.pg_attrdef d
              ON d.adrelid = a.attrelid AND d.adnum = a.attnum
            WHERE a.attrelid = pg_catalog.to_regclass(:table_name)
              AND a.attnum > 0 AND NOT a.attisdropped
            ORDER BY a.attnum
        """), {"table_name": f"public.{name}"}).all()
        actual = {tuple(row[:4]) for row in columns}
        if (actual != set(LEGACY_COLUMNS[name])
                or any(row[4] or row[5] for row in columns)):
            raise RuntimeError(f"Phase-0 refuses unexpected legacy columns in {name}")
        pk = inspector.get_pk_constraint(name, schema="public")["constrained_columns"]
        if pk != [LEGACY_COLUMNS[name][0][0]]:
            raise RuntimeError(f"Phase-0 refuses unexpected legacy primary key in {name}")
        foreign_keys = inspector.get_foreign_keys(name, schema="public")
        actual_keys = set()
        for fk in foreign_keys:
            if (len(fk["constrained_columns"]) != 1
                    or len(fk["referred_columns"]) != 1
                    or fk.get("referred_schema") not in (None, "public")
                    or fk.get("options")):
                raise RuntimeError(f"Phase-0 refuses unexpected legacy foreign key in {name}")
            actual_keys.add((
                fk["constrained_columns"][0], fk["referred_table"],
                fk["referred_columns"][0],
            ))
        if (actual_keys != LEGACY_FOREIGN_KEYS[name]
                or len(actual_keys) != len(foreign_keys)
                or inspector.get_unique_constraints(name, schema="public")
                or inspector.get_check_constraints(name, schema="public")
                or inspector.get_indexes(name, schema="public")):
            raise RuntimeError(f"Phase-0 refuses unexpected legacy constraints in {name}")


def _validate_post_upgrade_shape() -> None:
    """Compare fixed source expectations under downgrade's existing locks.

    This adapter is deliberately limited to PostgreSQL 16 and this revision's
    plain columns, immediate constraints and btree indexes. Unknown forms refuse.
    """
    bind = op.get_bind()
    if int(bind.execute(sa.text("SHOW server_version_num")).scalar_one()) // 10000 != 16:
        raise RuntimeError("Phase-0 refuses unsupported downgrade catalog version")
    columns = bind.execute(sa.text("""
        SELECT c.relname, a.attname, tn.nspname, t.typname, a.atttypmod,
               t.typtype, e.extname, en.nspname, cn.nspname, co.collname,
               NOT a.attnotnull, pg_catalog.pg_get_expr(d.adbin, d.adrelid),
               a.attidentity, a.attgenerated,
               EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep
                       WHERE dep.classid = 'pg_catalog.pg_attrdef'::regclass
                         AND dep.objid = d.oid
                         AND dep.refclassid = 'pg_catalog.pg_proc'::regclass
                         AND dep.refobjid <> 'pg_catalog.now()'::regprocedure) AS other_default_function
        FROM pg_catalog.pg_attribute a
        JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_catalog.pg_type t ON t.oid = a.atttypid
        JOIN pg_catalog.pg_namespace tn ON tn.oid = t.typnamespace
        LEFT JOIN pg_catalog.pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
        LEFT JOIN pg_catalog.pg_collation co ON co.oid = a.attcollation
        LEFT JOIN pg_catalog.pg_namespace cn ON cn.oid = co.collnamespace
        LEFT JOIN pg_catalog.pg_depend ed ON ed.classid = 'pg_catalog.pg_type'::regclass
          AND ed.objid = t.oid AND ed.refclassid = 'pg_catalog.pg_extension'::regclass AND ed.deptype = 'e'
        LEFT JOIN pg_catalog.pg_extension e ON e.oid = ed.refobjid
        LEFT JOIN pg_catalog.pg_namespace en ON en.oid = e.extnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname <> 'alembic_version'
          AND a.attnum > 0 AND NOT a.attisdropped
    """)).all()
    expected_columns = Counter(
        (table, name, *POST_TYPE_FACTS[declared], nullable, default, "", "", False)
        for table, rows in POST_UPGRADE_COLUMNS.items()
        for name, declared, nullable, default in rows
    )
    _require_post_upgrade_records("columns", Counter(tuple(row) for row in columns), expected_columns)
    enum_rows = bind.execute(sa.text("""
        SELECT t.typname, array_agg(e.enumlabel ORDER BY e.enumsortorder)
        FROM pg_catalog.pg_type t JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        JOIN pg_catalog.pg_enum e ON e.enumtypid = t.oid
        WHERE n.nspname = 'public' GROUP BY t.typname
    """)).all()
    enums = {name: tuple(labels) for name, labels in enum_rows if name in OWNED_ENUM_TYPES}
    if enums != POST_UPGRADE_ENUMS:
        raise RuntimeError("Phase-0 refuses changed revision-owned enum labels")
    constraints = bind.execute(sa.text("""
        SELECT k.oid, k.conrelid, k.conindid, c.relname AS table_name, k.contype,
               ARRAY(SELECT a.attname FROM unnest(k.conkey) WITH ORDINALITY x(num, ord)
                     LEFT JOIN pg_catalog.pg_attribute a ON a.attrelid = k.conrelid AND a.attnum = x.num
                     ORDER BY x.ord) AS keys,
               rn.nspname AS remote_schema, rc.relname AS remote_table,
               ARRAY(SELECT a.attname FROM unnest(k.confkey) WITH ORDINALITY x(num, ord)
                     LEFT JOIN pg_catalog.pg_attribute a ON a.attrelid = k.confrelid AND a.attnum = x.num
                     ORDER BY x.ord) AS remote_keys,
               k.confupdtype, k.confdeltype, k.confmatchtype,
               k.condeferrable, k.condeferred, k.convalidated,
               k.conislocal, k.coninhcount, k.conparentid
        FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid = k.conrelid
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_catalog.pg_class rc ON rc.oid = k.confrelid
        LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid = rc.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname <> 'alembic_version'
    """)).mappings().all()
    actual_constraints = Counter()
    supporting = {}
    for row in constraints:
        kind = row["contype"]
        if (kind not in {"p", "u", "f"} or row["condeferrable"] or row["condeferred"]
                or not row["convalidated"] or not row["conislocal"]
                or row["coninhcount"] != 0 or row["conparentid"] != 0):
            raise RuntimeError(f"Phase-0 refuses unexpected post-upgrade constraints in {row['table_name']}: timing/validation/kind")
        if kind == "f":
            if (row["remote_schema"] != "public" or row["confupdtype"] != "a"
                    or row["confdeltype"] != "a" or row["confmatchtype"] != "s"):
                raise RuntimeError(f"Phase-0 refuses unexpected post-upgrade constraints in {row['table_name']}: qualified target/action/match")
            target, remote_keys = row["remote_table"], tuple(row["remote_keys"])
        else:
            target, remote_keys = None, ()
            index_oid = row["conindid"]
            if not index_oid or index_oid in supporting:
                raise RuntimeError("Phase-0 refuses ambiguous constraint index ownership")
            supporting[index_oid] = (row["conrelid"], kind, tuple(row["keys"]))
        actual_constraints[(row["table_name"], kind, tuple(row["keys"]), target, remote_keys)] += 1
    expected_constraints = Counter((table, *row) for table, rows in POST_UPGRADE_CONSTRAINTS.items() for row in rows)
    _require_post_upgrade_records("constraints", actual_constraints, expected_constraints)
    indexes = bind.execute(sa.text("""
        SELECT i.indexrelid, i.indrelid, c.relname AS table_name, ic.relname AS index_name,
               am.amname, i.indisunique, i.indisprimary, i.indisexclusion,
               i.indimmediate, i.indisvalid, i.indisready, i.indislive, i.indnullsnotdistinct,
               i.indnkeyatts, i.indnatts,
               pg_catalog.pg_get_expr(i.indexprs, i.indrelid) AS expressions,
               pg_catalog.pg_get_expr(i.indpred, i.indrelid) AS predicate,
               ARRAY(SELECT a.attname FROM unnest(i.indkey) WITH ORDINALITY x(num, ord)
                     LEFT JOIN pg_catalog.pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = x.num
                     ORDER BY x.ord) AS keys,
               i.indoption::smallint[] AS options,
               ARRAY(SELECT coalesce(nc.nspname || '.' || co.collname, '')
                     FROM unnest(i.indcollation) WITH ORDINALITY x(oid, ord)
                     LEFT JOIN pg_catalog.pg_collation co ON co.oid = x.oid
                     LEFT JOIN pg_catalog.pg_namespace nc ON nc.oid = co.collnamespace ORDER BY x.ord) AS collations,
               (SELECT jsonb_agg(jsonb_build_array(ns.nspname, oc.opcname, nt.nspname, t.typname,
                           oc.opcdefault, ma.amname, nf.nspname, f.opfname) ORDER BY x.ord)
                FROM unnest(i.indclass) WITH ORDINALITY x(oid, ord)
                JOIN pg_catalog.pg_opclass oc ON oc.oid = x.oid
                JOIN pg_catalog.pg_namespace ns ON ns.oid = oc.opcnamespace
                JOIN pg_catalog.pg_type t ON t.oid = oc.opcintype
                JOIN pg_catalog.pg_namespace nt ON nt.oid = t.typnamespace
                JOIN pg_catalog.pg_am ma ON ma.oid = oc.opcmethod
                JOIN pg_catalog.pg_opfamily f ON f.oid = oc.opcfamily
                JOIN pg_catalog.pg_namespace nf ON nf.oid = f.opfnamespace) AS opclasses
        FROM pg_catalog.pg_index i JOIN pg_catalog.pg_class c ON c.oid = i.indrelid
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_catalog.pg_class ic ON ic.oid = i.indexrelid
        JOIN pg_catalog.pg_am am ON am.oid = ic.relam
        WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname <> 'alembic_version'
    """)).mappings().all()
    actual_indexes = Counter()
    seen_supporting = set()
    for row in indexes:
        owner = supporting.get(row["indexrelid"])
        if owner is not None:
            if owner[0] != row["indrelid"] or owner[2] != tuple(row["keys"]):
                raise RuntimeError("Phase-0 refuses mismatched constraint supporting index")
            label = ("constraint", owner[1])
            seen_supporting.add(row["indexrelid"])
        else:
            label = ("standalone", row["index_name"])
        actual_indexes[(row["table_name"], label, tuple(row["keys"]), row["amname"],
                        row["indisunique"], row["indisprimary"], row["indisexclusion"],
                        row["indimmediate"], row["indisvalid"], row["indisready"], row["indislive"],
                        row["indnullsnotdistinct"], row["indnkeyatts"], row["indnatts"],
                        row["expressions"], row["predicate"], tuple(row["options"]),
                        tuple(row["collations"]), tuple(tuple(value) for value in (row["opclasses"] or [])))] += 1
    if seen_supporting != set(supporting):
        raise RuntimeError("Phase-0 refuses missing constraint supporting index")
    _require_post_upgrade_records("indexes", actual_indexes, _expected_post_upgrade_indexes())


def _require_post_upgrade_records(category, actual, expected):
    differences = (actual - expected) + (expected - actual)
    if differences:
        tables = ", ".join(sorted({record[0] for record in differences}))
        raise RuntimeError(f"Phase-0 refuses unexpected post-upgrade {category} in {tables}: record/set mismatch")


def _expected_post_upgrade_indexes():
    # PostgreSQL 16 defaults: varchar is binary compatible with text; enum uses anyenum.
    # These qualified opclasses/families come from pg_opclass.dat, not the observed DB.
    classes = {
        "uuid": ("uuid_ops", "uuid", "uuid_ops"),
        "varchar": ("text_ops", "text", "text_ops"),
        "text": ("text_ops", "text", "text_ops"),
        "date": ("date_ops", "date", "datetime_ops"),
        "timestamptz": ("timestamptz_ops", "timestamptz", "datetime_ops"),
        "enum": ("enum_ops", "anyenum", "enum_ops"),
    }
    result = Counter()
    for table, columns in POST_UPGRADE_COLUMNS.items():
        types = {name: POST_TYPE_FACTS[declared] for name, declared, _, _ in columns}
        expected = [(('standalone', name), keys, False, False) for name, keys in POST_UPGRADE_INDEXES[table]]
        expected += [(('constraint', kind), keys, True, kind == 'p')
                     for kind, keys, _, _ in POST_UPGRADE_CONSTRAINTS[table] if kind in {'p', 'u'}]
        for label, keys, unique, primary in expected:
            collations, opclasses = [], []
            for name in keys:
                fact = types[name]
                collations.append('.'.join(fact[6:]) if fact[6] is not None else '')
                opc, input_type, family = classes['enum' if fact[3] == 'e' else fact[1]]
                opclasses.append(('pg_catalog', opc, 'pg_catalog', input_type, True, 'btree', 'pg_catalog', family))
            result[(table, label, keys, 'btree', unique, primary, False, True, True, True, True,
                    False, len(keys), len(keys), None, None, (0,) * len(keys),
                    tuple(collations), tuple(opclasses))] += 1
    return result


def _check_enum_name_collisions() -> None:
    existing = set(op.get_bind().execute(sa.text("""
        SELECT t.typname FROM pg_catalog.pg_type t
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public'
    """)).scalars())
    if existing & (OWNED_ENUM_TYPES | {EMPTY_BOOTSTRAP_MARKER_TYPE}):
        raise RuntimeError("Phase-0 refuses a pre-existing revision type name")


def _owned_enum_oids() -> dict[str, int]:
    existing = dict(op.get_bind().execute(sa.text("""
        SELECT t.typname, t.oid FROM pg_catalog.pg_type t
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public' AND t.typtype = 'e'
    """)).all())
    if OWNED_ENUM_TYPES - existing.keys():
        raise RuntimeError("Phase-0 refuses missing revision-owned enum types")
    return {name: existing[name] for name in OWNED_ENUM_TYPES}


def _ownership_labels(fresh: bool, enum_oids: dict[str, int]) -> list[str]:
    return [
        "d4787e8e3629:preservation-v1", "fresh" if fresh else "legacy",
        *[f"enum:{name}:{enum_oids[name]}" for name in sorted(OWNED_ENUM_TYPES)],
    ]


def _record_ownership(fresh: bool) -> None:
    # Every listed enum name was absent before this revision. This is an exact
    # ownership list, never permission to remove arbitrary public enum types.
    # OIDs also reject a later same-name replacement of a revision-created type.
    enum_oids = _owned_enum_oids()
    labels = ", ".join(f"'{label}'" for label in _ownership_labels(fresh, enum_oids))
    op.execute(f'CREATE TYPE public."{EMPTY_BOOTSTRAP_MARKER_TYPE}" AS ENUM ({labels})')


def _is_empty_database_bootstrap() -> bool:
    labels = list(op.get_bind().execute(sa.text("""
        SELECT e.enumlabel FROM pg_catalog.pg_enum e
        JOIN pg_catalog.pg_type t ON t.oid = e.enumtypid
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE n.nspname = 'public' AND t.typname = :marker
        ORDER BY e.enumsortorder
    """), {"marker": EMPTY_BOOTSTRAP_MARKER_TYPE}).scalars())
    enum_oids = _owned_enum_oids()
    for fresh in (True, False):
        if labels == _ownership_labels(fresh, enum_oids):
            return fresh
    raise RuntimeError("Phase-0 refuses downgrade without recognised revision ownership")


def _prepare_legacy_baseline() -> bool:
    """Admit fresh or recognised empty-core legacy schemas; preserve directories."""
    existing = _public_tables()
    fresh = not existing
    allowed = LEGACY_CORE_TABLES | LEGACY_DIRECTORY_TABLES
    if existing - allowed or (not fresh and LEGACY_CORE_TABLES - existing):
        raise RuntimeError("Phase-0 refuses incomplete or unexpected legacy tables")
    _lock_tables(existing)
    _require_no_other_writer_transactions()
    if _public_tables() != existing:
        raise RuntimeError("Phase-0 refuses a concurrently changed legacy schema")
    _check_enum_name_collisions()
    if not fresh:
        _validate_legacy_shape(existing)
        _require_empty(LEGACY_CORE_TABLES, "upgrade")
    # No persistent DDL occurs until admission and locked emptiness checks pass.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    if fresh:
        _create_legacy_core_tables()
    _create_missing_directory_tables(existing)
    return fresh


def upgrade() -> None:
    """Support fresh/empty-core installations, refusing populated older schemas."""
    with _preservation_transaction():
        fresh = _prepare_legacy_baseline()
        _upgrade_schema()
        _record_ownership(fresh)


def downgrade() -> None:
    """Refuse records before dropping/changing tables; preserve legacy directories."""
    with _preservation_transaction():
        expected = LEGACY_CORE_TABLES | LEGACY_DIRECTORY_TABLES | PHASE0_NEW_TABLES
        if _public_tables() != expected:
            raise RuntimeError("Phase-0 refuses incomplete or unexpected downgrade tables")
        _lock_tables(expected)
        _require_no_other_writer_transactions()
        if _public_tables() != expected:
            raise RuntimeError("Phase-0 refuses a concurrently changed downgrade schema")
        fresh = _is_empty_database_bootstrap()
        affected = LEGACY_CORE_TABLES | PHASE0_NEW_TABLES
        if fresh:
            affected |= LEGACY_DIRECTORY_TABLES
        _require_empty(affected, "downgrade")
        _validate_post_upgrade_shape()
        _downgrade_schema()
        if fresh:
            for table in (
                "prescriptions", "mbs_claims", "clinical_diagnoses", "encounters",
                "patients", "mbs_directory", "snomed_directory",
            ):
                op.drop_table(table, schema="public")
        # Legacy directories remain even if this upgrade originally created
        # them. Their rows are never cleared, backfilled, transformed or dropped.
        for name in sorted(OWNED_ENUM_TYPES):
            op.execute(f'DROP TYPE public."{name}" RESTRICT')
        op.execute(f'DROP TYPE public."{EMPTY_BOOTSTRAP_MARKER_TYPE}" RESTRICT')


def _drop_foreign_key_for_column(table_name: str, column_name: str) -> None:
    """Drop one PostgreSQL-named FK emitted from an unnamed Alembic FK."""
    matches = [
        foreign_key
        for foreign_key in sa.inspect(op.get_bind()).get_foreign_keys(table_name, schema="public")
        if foreign_key.get("constrained_columns") == [column_name]
    ]
    if len(matches) != 1 or not matches[0].get("name"):
        raise RuntimeError(
            "Expected exactly one named foreign key for "
            f"{table_name}.{column_name}; found {len(matches)}"
        )
    op.drop_constraint(
        matches[0]["name"], table_name, type_="foreignkey", schema="public"
    )


def _upgrade_schema() -> None:
    """Original generated schema operations, after preservation admission."""
    # Pre-create enum types for add_column on existing tables (PostgreSQL requires type before column)
    op.execute("CREATE TYPE encounterstatus AS ENUM ('Draft', 'InProgress', 'Finalized', 'Amended')")
    op.execute("CREATE TYPE templatetype AS ENUM ('SOAP', 'Procedure', 'MentalHealth', 'CDM', 'GPCCMP', 'HealthAssessment', 'Antenatal', 'WoundCare')")
    op.execute("CREATE TYPE claimtype AS ENUM ('BulkBill', 'PatientClaim', 'DVA', 'WorkCover', 'TAC', 'ECLIPSE')")
    op.execute("CREATE TYPE claimstatus AS ENUM ('Draft', 'Submitted', 'Accepted', 'Rejected', 'Paid')")
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('practices',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('abn', sa.String(length=20), nullable=True),
    sa.Column('address_line1', sa.String(length=255), nullable=True),
    sa.Column('address_line2', sa.String(length=255), nullable=True),
    sa.Column('address_suburb', sa.String(length=100), nullable=True),
    sa.Column('address_state', sa.String(length=10), nullable=True),
    sa.Column('address_postcode', sa.String(length=10), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('logo_url', sa.String(length=500), nullable=True),
    sa.Column('timezone', sa.String(length=50), nullable=True),
    sa.Column('hive_mind_opt_in', sa.Boolean(), nullable=True),
    sa.Column('practice_embedding', pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True),
    sa.Column('specialty_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('asgc_ra_code', sa.String(length=10), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('proda_device_cert_path', sa.String(length=500), nullable=True),
    sa.Column('proda_cert_expiry', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('appointment_types',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('default_duration', sa.Integer(), nullable=True),
    sa.Column('color_hex', sa.String(length=7), nullable=True),
    sa.Column('is_bookable_online', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_appointment_types_practice_id', 'appointment_types', ['practice_id'], unique=False)
    op.create_table('community_encounters',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('source_practice_id', sa.UUID(), nullable=True),
    sa.Column('deidentified_text', sa.Text(), nullable=False),
    sa.Column('encounter_embedding', pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True),
    sa.Column('mbs_item', sa.String(length=20), nullable=True),
    sa.Column('snomed_codes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('gp_tier', sa.Enum('Tier1_Gold', 'Tier2', 'Tier3', name='gptier'), nullable=True),
    sa.Column('practice_specialty_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('practice_asgc_ra_code', sa.String(length=10), nullable=True),
    sa.Column('practice_latitude', sa.Float(), nullable=True),
    sa.Column('practice_longitude', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['source_practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('practice_locations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('address_line1', sa.String(length=255), nullable=True),
    sa.Column('address_suburb', sa.String(length=100), nullable=True),
    sa.Column('address_state', sa.String(length=10), nullable=True),
    sa.Column('address_postcode', sa.String(length=10), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('waiting_rooms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_practice_locations_practice_id', 'practice_locations', ['practice_id'], unique=False)
    op.create_table('allergies',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('substance', sa.String(length=255), nullable=False),
    sa.Column('reaction', sa.Text(), nullable=True),
    sa.Column('severity', sa.String(length=50), nullable=True),
    sa.Column('snomed_code', sa.String(length=50), nullable=True),
    sa.Column('recorded_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_allergies_patient_id', 'allergies', ['patient_id'], unique=False)
    op.create_table('ihi_records',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('ihi_number', sa.String(length=20), nullable=False),
    sa.Column('ihi_status', sa.String(length=50), nullable=True),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('source', sa.Enum('Manual', 'HI_Service', name='ihisource'), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ihi_records_patient_id', 'ihi_records', ['patient_id'], unique=False)
    op.create_table('immunisations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('vaccine_name', sa.String(length=255), nullable=False),
    sa.Column('dose_number', sa.String(length=10), nullable=True),
    sa.Column('date_given', sa.Date(), nullable=True),
    sa.Column('batch_number', sa.String(length=50), nullable=True),
    sa.Column('site', sa.String(length=50), nullable=True),
    sa.Column('route', sa.String(length=50), nullable=True),
    sa.Column('air_notification_sent', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_immunisations_patient_id', 'immunisations', ['patient_id'], unique=False)
    op.create_table('patient_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('category', sa.Enum('Medical', 'Surgical', 'Family', 'Social', name='historycategory'), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('date_recorded', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_patient_history_patient_id', 'patient_history', ['patient_id'], unique=False)
    op.create_table('patient_qr_tokens',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('token_hash', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    op.create_index('ix_patient_qr_tokens_patient_id', 'patient_qr_tokens', ['patient_id'], unique=False)
    op.create_table('practitioners',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('provider_number', sa.String(length=20), nullable=True),
    sa.Column('prescriber_number', sa.String(length=20), nullable=True),
    sa.Column('ahpra_number', sa.String(length=20), nullable=True),
    sa.Column('hpi_i', sa.String(length=20), nullable=True),
    sa.Column('specialty', sa.String(length=100), nullable=True),
    sa.Column('default_location_id', sa.UUID(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['default_location_id'], ['practice_locations.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_practitioners_practice_id', 'practitioners', ['practice_id'], unique=False)
    op.create_table('sms_log',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=True),
    sa.Column('direction', sa.Enum('Outbound', 'Inbound', name='smsdirection'), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('message_body', sa.Text(), nullable=False),
    sa.Column('sms_type', sa.Enum('AppointmentReminder', 'Confirmation', 'ResultNotification', 'Recall', 'Bulk', 'Custom', name='smstype'), nullable=True),
    sa.Column('status', sa.Enum('Queued', 'Sent', 'Delivered', 'Failed', 'Replied', name='smsstatus'), nullable=True),
    sa.Column('clicksend_message_id', sa.String(length=100), nullable=True),
    sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sms_log_patient_id', 'sms_log', ['patient_id'], unique=False)
    op.create_index('ix_sms_log_practice_id', 'sms_log', ['practice_id'], unique=False)
    op.create_table('practitioner_schedules',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practitioner_id', sa.UUID(), nullable=False),
    sa.Column('location_id', sa.UUID(), nullable=True),
    sa.Column('day_of_week', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('slot_duration_minutes', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['practice_locations.id'], ),
    sa.ForeignKeyConstraint(['practitioner_id'], ['practitioners.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_practitioner_schedules_practitioner_id', 'practitioner_schedules', ['practitioner_id'], unique=False)
    op.create_table('scanned_documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('triaged_to', sa.UUID(), nullable=True),
    sa.Column('document_type', sa.Enum('SpecialistLetter', 'Report', 'Correspondence', 'Other', name='documenttype'), nullable=False),
    sa.Column('file_url', sa.String(length=500), nullable=False),
    sa.Column('scanned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('triage_status', sa.Enum('Pending', 'Triaged', 'Reviewed', name='triagestatus'), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.ForeignKeyConstraint(['triaged_to'], ['practitioners.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scanned_documents_patient_id', 'scanned_documents', ['patient_id'], unique=False)
    op.create_table('schedule_overrides',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practitioner_id', sa.UUID(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('is_unavailable', sa.Boolean(), nullable=True),
    sa.Column('override_start', sa.Time(), nullable=True),
    sa.Column('override_end', sa.Time(), nullable=True),
    sa.Column('reason', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['practitioner_id'], ['practitioners.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_schedule_overrides_practitioner_id_date', 'schedule_overrides', ['practitioner_id', 'date'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('GP', 'Receptionist', 'Nurse', 'Admin', 'PracticeOwner', name='userrole'), nullable=False),
    sa.Column('practitioner_id', sa.UUID(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.ForeignKeyConstraint(['practitioner_id'], ['practitioners.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_index('ix_users_practice_id', 'users', ['practice_id'], unique=False)
    op.create_table('appointments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('location_id', sa.UUID(), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('practitioner_id', sa.UUID(), nullable=False),
    sa.Column('appointment_type_id', sa.UUID(), nullable=True),
    sa.Column('booked_by', sa.UUID(), nullable=True),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('Booked', 'Confirmed', 'Arrived', 'InConsult', 'Completed', 'Cancelled', 'NoShow', 'DNA', name='appointmentstatus'), nullable=True),
    sa.Column('reason', sa.String(length=500), nullable=True),
    sa.Column('notes', sa.String(length=1000), nullable=True),
    sa.Column('booked_via', sa.Enum('Receptionist', 'Online', 'Phone', 'Kiosk', 'App', name='bookingchannel'), nullable=True),
    sa.Column('waiting_room', sa.String(length=50), nullable=True),
    sa.Column('queue_position', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['appointment_type_id'], ['appointment_types.id'], ),
    sa.ForeignKeyConstraint(['booked_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['practice_locations.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.ForeignKeyConstraint(['practitioner_id'], ['practitioners.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_appointments_patient_id', 'appointments', ['patient_id'], unique=False)
    op.create_index('ix_appointments_practice_id', 'appointments', ['practice_id'], unique=False)
    op.create_index('ix_appointments_practitioner_id', 'appointments', ['practitioner_id'], unique=False)
    op.create_index('ix_appointments_start_time', 'appointments', ['start_time'], unique=False)
    op.create_table('call_log',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('caller_number', sa.String(length=20), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=True),
    sa.Column('answered_by', sa.UUID(), nullable=True),
    sa.Column('call_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('call_type', sa.Enum('Inbound', 'Outbound', 'Telehealth', 'Missed', name='calltype'), nullable=False),
    sa.Column('notes', sa.String(length=1000), nullable=True),
    sa.ForeignKeyConstraint(['answered_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_call_log_practice_id', 'call_log', ['practice_id'], unique=False)
    op.create_table('checkin_events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('appointment_id', sa.UUID(), nullable=True),
    sa.Column('checkin_method', sa.Enum('Details', 'QR', 'NFC', 'FacialRecognition', name='checkinmethod'), nullable=False),
    sa.Column('checkin_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('waiting_room_assigned', sa.String(length=50), nullable=True),
    sa.Column('kiosk_id', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_checkin_events_patient_id', 'checkin_events', ['patient_id'], unique=False)
    op.create_table('internal_messages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('sender_id', sa.UUID(), nullable=False),
    sa.Column('recipient_id', sa.UUID(), nullable=True),
    sa.Column('recipient_role', sa.String(length=50), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=True),
    sa.Column('appointment_id', sa.UUID(), nullable=True),
    sa.Column('subject', sa.String(length=255), nullable=True),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('priority', sa.Enum('Normal', 'Urgent', 'Critical', name='messagepriority'), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_internal_messages_practice_id', 'internal_messages', ['practice_id'], unique=False)
    op.create_index('ix_internal_messages_recipient_id', 'internal_messages', ['recipient_id'], unique=False)
    op.create_table('care_plans',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('encounter_id', sa.UUID(), nullable=True),
    sa.Column('plan_type', sa.Enum('GPCCMP', 'MHTP', 'HealthAssessment45', 'HealthAssessment75', 'ATSI_HA', 'Antenatal', name='careplantype'), nullable=False),
    sa.Column('mbs_item', sa.String(length=20), nullable=True),
    sa.Column('status', sa.Enum('Draft', 'Active', 'Review_Due', 'Completed', name='careplanstatus'), nullable=True),
    sa.Column('valid_until', sa.Date(), nullable=True),
    sa.Column('review_date', sa.Date(), nullable=True),
    sa.Column('plan_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_care_plans_patient_id', 'care_plans', ['patient_id'], unique=False)
    op.create_index('ix_care_plans_practice_id', 'care_plans', ['practice_id'], unique=False)
    op.create_table('clinical_images',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('encounter_id', sa.UUID(), nullable=True),
    sa.Column('image_url', sa.String(length=500), nullable=False),
    sa.Column('caption', sa.Text(), nullable=True),
    sa.Column('body_site', sa.String(length=100), nullable=True),
    sa.Column('captured_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_clinical_images_patient_id', 'clinical_images', ['patient_id'], unique=False)
    op.create_table('consent_forms',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('encounter_id', sa.UUID(), nullable=True),
    sa.Column('form_type', sa.String(length=100), nullable=False),
    sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('signature_data', sa.Text(), nullable=True),
    sa.Column('document_path', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_consent_forms_patient_id', 'consent_forms', ['patient_id'], unique=False)
    op.create_table('invoices',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('encounter_id', sa.UUID(), nullable=True),
    sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('paid_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('status', sa.Enum('Draft', 'Issued', 'Paid', 'Overdue', 'Cancelled', name='invoicestatus'), nullable=True),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_invoices_patient_id', 'invoices', ['patient_id'], unique=False)
    op.create_table('mhr_uploads',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('encounter_id', sa.UUID(), nullable=True),
    sa.Column('document_type', sa.Enum('SharedHealthSummary', 'EventSummary', 'DischargeSummary', 'Other', name='mhrdocumenttype'), nullable=False),
    sa.Column('upload_status', sa.String(length=50), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('mhr_document_id', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_mhr_uploads_patient_id', 'mhr_uploads', ['patient_id'], unique=False)
    op.create_table('rag_feedback',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('encounter_id', sa.UUID(), nullable=True),
    sa.Column('query_embedding', pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True),
    sa.Column('retrieved_community_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('was_accepted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rag_feedback_practice_id', 'rag_feedback', ['practice_id'], unique=False)
    op.create_table('referrals',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('practitioner_id', sa.UUID(), nullable=True),
    sa.Column('encounter_id', sa.UUID(), nullable=True),
    sa.Column('referral_to', sa.String(length=255), nullable=True),
    sa.Column('specialty', sa.String(length=100), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('urgency', sa.String(length=50), nullable=True),
    sa.Column('status', sa.Enum('Draft', 'Sent', 'Accepted', 'Completed', name='referralstatus'), nullable=True),
    sa.Column('letter_document_path', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.ForeignKeyConstraint(['practitioner_id'], ['practitioners.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_referrals_patient_id', 'referrals', ['patient_id'], unique=False)
    op.create_table('test_requests',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('practitioner_id', sa.UUID(), nullable=True),
    sa.Column('encounter_id', sa.UUID(), nullable=True),
    sa.Column('request_type', sa.Enum('Pathology', 'Radiology', 'Specialist', 'Other', name='requesttype'), nullable=False),
    sa.Column('request_text', sa.Text(), nullable=True),
    sa.Column('urgency', sa.String(length=50), nullable=True),
    sa.Column('status', sa.Enum('Pending', 'ResultReceived', 'Reviewed', name='requeststatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.ForeignKeyConstraint(['practitioner_id'], ['practitioners.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_test_requests_patient_id', 'test_requests', ['patient_id'], unique=False)
    op.create_table('results',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('test_request_id', sa.UUID(), nullable=True),
    sa.Column('reviewed_by', sa.UUID(), nullable=True),
    sa.Column('result_source', sa.Enum('PIT', 'HL7', 'Manual', 'Scan', name='resultsource'), nullable=False),
    sa.Column('lab_name', sa.String(length=255), nullable=True),
    sa.Column('specimen_date', sa.Date(), nullable=True),
    sa.Column('report_date', sa.Date(), nullable=True),
    sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('status', sa.Enum('New', 'Reviewed', 'ActionRequired', 'Filed', name='resultstatus'), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('raw_message', sa.Text(), nullable=True),
    sa.Column('parsed_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_abnormal', sa.Boolean(), nullable=True),
    sa.Column('ai_summary', sa.Text(), nullable=True),
    sa.Column('display_pdf_url', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.ForeignKeyConstraint(['reviewed_by'], ['practitioners.id'], ),
    sa.ForeignKeyConstraint(['test_request_id'], ['test_requests.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_results_patient_id', 'results', ['patient_id'], unique=False)
    op.create_index('ix_results_practice_id', 'results', ['practice_id'], unique=False)
    op.create_index('ix_results_status', 'results', ['status'], unique=False)
    op.create_table('reminders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('practice_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('practitioner_id', sa.UUID(), nullable=True),
    sa.Column('triggered_by_result_id', sa.UUID(), nullable=True),
    sa.Column('reminder_type', sa.Enum('ResultFollowUp', 'Recall', 'ReviewAppointment', 'CarePlanReview', 'Custom', name='remindertype'), nullable=False),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('is_dismissed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['practice_id'], ['practices.id'], ),
    sa.ForeignKeyConstraint(['practitioner_id'], ['practitioners.id'], ),
    sa.ForeignKeyConstraint(['triggered_by_result_id'], ['results.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminders_patient_id', 'reminders', ['patient_id'], unique=False)
    op.create_index('ix_reminders_practice_id', 'reminders', ['practice_id'], unique=False)
    op.create_table('result_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('result_id', sa.UUID(), nullable=False),
    sa.Column('test_name', sa.String(length=255), nullable=False),
    sa.Column('value', sa.String(length=100), nullable=True),
    sa.Column('units', sa.String(length=50), nullable=True),
    sa.Column('reference_range', sa.String(length=100), nullable=True),
    sa.Column('flag', sa.Enum('Normal', 'Low', 'High', 'Critical', name='resultflag'), nullable=True),
    sa.Column('loinc_code', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['result_id'], ['results.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_result_items_result_id', 'result_items', ['result_id'], unique=False)
    op.add_column('clinical_diagnoses', sa.Column('practice_id', sa.UUID(), nullable=False))
    op.add_column('clinical_diagnoses', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('clinical_diagnoses', sa.Column('onset_date', sa.Date(), nullable=True))
    op.add_column('clinical_diagnoses', sa.Column('resolved_date', sa.Date(), nullable=True))
    op.add_column('clinical_diagnoses', sa.Column('severity', sa.String(length=50), nullable=True))
    op.alter_column('clinical_diagnoses', 'patient_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.create_index('ix_clinical_diagnoses_patient_id', 'clinical_diagnoses', ['patient_id'], unique=False)
    op.create_index('ix_clinical_diagnoses_practice_id', 'clinical_diagnoses', ['practice_id'], unique=False)
    op.create_foreign_key(None, 'clinical_diagnoses', 'practices', ['practice_id'], ['id'])
    op.add_column('encounters', sa.Column('practice_id', sa.UUID(), nullable=False))
    op.add_column('encounters', sa.Column('practitioner_id', sa.UUID(), nullable=True))
    op.add_column('encounters', sa.Column('appointment_id', sa.UUID(), nullable=True))
    op.add_column('encounters', sa.Column('status', sa.Enum('Draft', 'InProgress', 'Finalized', 'Amended', name='encounterstatus'), nullable=True))
    op.add_column('encounters', sa.Column('template_type', sa.Enum('SOAP', 'Procedure', 'MentalHealth', 'CDM', 'GPCCMP', 'HealthAssessment', 'Antenatal', 'WoundCare', name='templatetype'), nullable=True))
    op.add_column('encounters', sa.Column('is_shared_to_hive', sa.Boolean(), nullable=True))
    op.add_column('encounters', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('encounters', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.alter_column('encounters', 'patient_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('encounters', 'google_doc_id',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.create_index('ix_encounters_patient_id', 'encounters', ['patient_id'], unique=False)
    op.create_index('ix_encounters_practice_id', 'encounters', ['practice_id'], unique=False)
    op.create_foreign_key(None, 'encounters', 'practices', ['practice_id'], ['id'])
    op.create_foreign_key(None, 'encounters', 'appointments', ['appointment_id'], ['id'])
    op.create_foreign_key(None, 'encounters', 'practitioners', ['practitioner_id'], ['id'])
    op.add_column('mbs_claims', sa.Column('practice_id', sa.UUID(), nullable=False))
    op.add_column('mbs_claims', sa.Column('patient_id', sa.UUID(), nullable=False))
    op.add_column('mbs_claims', sa.Column('practitioner_id', sa.UUID(), nullable=True))
    op.add_column('mbs_claims', sa.Column('claim_type', sa.Enum('BulkBill', 'PatientClaim', 'DVA', 'WorkCover', 'TAC', 'ECLIPSE', name='claimtype'), nullable=True))
    op.add_column('mbs_claims', sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('mbs_claims', sa.Column('gateway_claim_id', sa.String(length=100), nullable=True))
    op.add_column('mbs_claims', sa.Column('claim_status', sa.Enum('Draft', 'Submitted', 'Accepted', 'Rejected', 'Paid', name='claimstatus'), nullable=True))
    op.add_column('mbs_claims', sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('mbs_claims', sa.Column('response_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_index('ix_mbs_claims_claim_status', 'mbs_claims', ['claim_status'], unique=False)
    op.create_index('ix_mbs_claims_patient_id', 'mbs_claims', ['patient_id'], unique=False)
    op.create_index('ix_mbs_claims_practice_id', 'mbs_claims', ['practice_id'], unique=False)
    op.create_foreign_key(None, 'mbs_claims', 'practices', ['practice_id'], ['id'])
    op.create_foreign_key(None, 'mbs_claims', 'patients', ['patient_id'], ['id'])
    op.create_foreign_key(None, 'mbs_claims', 'practitioners', ['practitioner_id'], ['id'])
    op.drop_column('mbs_claims', 'status')
    op.add_column('patients', sa.Column('practice_id', sa.UUID(), nullable=False))
    op.add_column('patients', sa.Column('dva_number', sa.String(length=20), nullable=True))
    op.add_column('patients', sa.Column('sex', sa.String(length=10), nullable=True))
    op.add_column('patients', sa.Column('gender_identity', sa.String(length=50), nullable=True))
    op.add_column('patients', sa.Column('indigenous_status', sa.String(length=50), nullable=True))
    op.add_column('patients', sa.Column('preferred_language', sa.String(length=50), nullable=True))
    op.add_column('patients', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('patients', sa.Column('phone_mobile', sa.String(length=20), nullable=True))
    op.add_column('patients', sa.Column('phone_home', sa.String(length=20), nullable=True))
    op.add_column('patients', sa.Column('address_line1', sa.String(length=255), nullable=True))
    op.add_column('patients', sa.Column('address_suburb', sa.String(length=100), nullable=True))
    op.add_column('patients', sa.Column('address_state', sa.String(length=10), nullable=True))
    op.add_column('patients', sa.Column('address_postcode', sa.String(length=10), nullable=True))
    op.add_column('patients', sa.Column('emergency_contact_name', sa.String(length=200), nullable=True))
    op.add_column('patients', sa.Column('emergency_contact_phone', sa.String(length=20), nullable=True))
    op.add_column('patients', sa.Column('emergency_contact_relationship', sa.String(length=50), nullable=True))
    op.add_column('patients', sa.Column('concession_type', sa.String(length=50), nullable=True))
    op.add_column('patients', sa.Column('consent_facial_recognition', sa.Boolean(), nullable=True))
    op.add_column('patients', sa.Column('face_embedding_id', sa.String(length=255), nullable=True))
    op.add_column('patients', sa.Column('sms_consent', sa.Boolean(), nullable=True))
    op.add_column('patients', sa.Column('sms_consent_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('patients', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('patients', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.create_index('ix_patients_last_name', 'patients', ['last_name'], unique=False)
    op.create_index('ix_patients_medicare_number', 'patients', ['medicare_number'], unique=False)
    op.create_index('ix_patients_practice_id', 'patients', ['practice_id'], unique=False)
    op.create_foreign_key(None, 'patients', 'practices', ['practice_id'], ['id'])
    op.add_column('prescriptions', sa.Column('practice_id', sa.UUID(), nullable=False))
    op.add_column('prescriptions', sa.Column('prescribed_by', sa.UUID(), nullable=True))
    op.add_column('prescriptions', sa.Column('pbs_code', sa.String(length=20), nullable=True))
    op.add_column('prescriptions', sa.Column('repeats', sa.String(length=10), nullable=True))
    op.add_column('prescriptions', sa.Column('quantity', sa.String(length=20), nullable=True))
    op.add_column('prescriptions', sa.Column('route', sa.String(length=50), nullable=True))
    op.add_column('prescriptions', sa.Column('frequency', sa.String(length=100), nullable=True))
    op.add_column('prescriptions', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('prescriptions', sa.Column('end_date', sa.Date(), nullable=True))
    op.add_column('prescriptions', sa.Column('erx_token', sa.String(length=255), nullable=True))
    op.add_column('prescriptions', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.alter_column('prescriptions', 'patient_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.create_index('ix_prescriptions_patient_id', 'prescriptions', ['patient_id'], unique=False)
    op.create_foreign_key(None, 'prescriptions', 'practitioners', ['prescribed_by'], ['id'])
    op.create_foreign_key(None, 'prescriptions', 'practices', ['practice_id'], ['id'])
    # ### end Alembic commands ###


def _downgrade_schema() -> None:
    """Original generated reverse schema operations, after locked row checks."""
    # ### commands auto generated by Alembic - please adjust! ###
    _drop_foreign_key_for_column("prescriptions", "prescribed_by")
    _drop_foreign_key_for_column("prescriptions", "practice_id")
    op.drop_index('ix_prescriptions_patient_id', table_name='prescriptions')
    op.alter_column('prescriptions', 'patient_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('prescriptions', 'created_at')
    op.drop_column('prescriptions', 'erx_token')
    op.drop_column('prescriptions', 'end_date')
    op.drop_column('prescriptions', 'start_date')
    op.drop_column('prescriptions', 'frequency')
    op.drop_column('prescriptions', 'route')
    op.drop_column('prescriptions', 'quantity')
    op.drop_column('prescriptions', 'repeats')
    op.drop_column('prescriptions', 'pbs_code')
    op.drop_column('prescriptions', 'prescribed_by')
    op.drop_column('prescriptions', 'practice_id')
    _drop_foreign_key_for_column("patients", "practice_id")
    op.drop_index('ix_patients_practice_id', table_name='patients')
    op.drop_index('ix_patients_medicare_number', table_name='patients')
    op.drop_index('ix_patients_last_name', table_name='patients')
    op.drop_column('patients', 'updated_at')
    op.drop_column('patients', 'created_at')
    op.drop_column('patients', 'sms_consent_date')
    op.drop_column('patients', 'sms_consent')
    op.drop_column('patients', 'face_embedding_id')
    op.drop_column('patients', 'consent_facial_recognition')
    op.drop_column('patients', 'concession_type')
    op.drop_column('patients', 'emergency_contact_relationship')
    op.drop_column('patients', 'emergency_contact_phone')
    op.drop_column('patients', 'emergency_contact_name')
    op.drop_column('patients', 'address_postcode')
    op.drop_column('patients', 'address_state')
    op.drop_column('patients', 'address_suburb')
    op.drop_column('patients', 'address_line1')
    op.drop_column('patients', 'phone_home')
    op.drop_column('patients', 'phone_mobile')
    op.drop_column('patients', 'email')
    op.drop_column('patients', 'preferred_language')
    op.drop_column('patients', 'indigenous_status')
    op.drop_column('patients', 'gender_identity')
    op.drop_column('patients', 'sex')
    op.drop_column('patients', 'dva_number')
    op.drop_column('patients', 'practice_id')
    op.add_column('mbs_claims', sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    _drop_foreign_key_for_column("mbs_claims", "practice_id")
    _drop_foreign_key_for_column("mbs_claims", "patient_id")
    _drop_foreign_key_for_column("mbs_claims", "practitioner_id")
    op.drop_index('ix_mbs_claims_practice_id', table_name='mbs_claims')
    op.drop_index('ix_mbs_claims_patient_id', table_name='mbs_claims')
    op.drop_index('ix_mbs_claims_claim_status', table_name='mbs_claims')
    op.drop_column('mbs_claims', 'response_data')
    op.drop_column('mbs_claims', 'submitted_at')
    op.drop_column('mbs_claims', 'claim_status')
    op.drop_column('mbs_claims', 'gateway_claim_id')
    op.drop_column('mbs_claims', 'amount')
    op.drop_column('mbs_claims', 'claim_type')
    op.drop_column('mbs_claims', 'practitioner_id')
    op.drop_column('mbs_claims', 'patient_id')
    op.drop_column('mbs_claims', 'practice_id')
    _drop_foreign_key_for_column("encounters", "practice_id")
    _drop_foreign_key_for_column("encounters", "appointment_id")
    _drop_foreign_key_for_column("encounters", "practitioner_id")
    op.drop_index('ix_encounters_practice_id', table_name='encounters')
    op.drop_index('ix_encounters_patient_id', table_name='encounters')
    op.alter_column('encounters', 'google_doc_id',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('encounters', 'patient_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('encounters', 'updated_at')
    op.drop_column('encounters', 'created_at')
    op.drop_column('encounters', 'is_shared_to_hive')
    op.drop_column('encounters', 'template_type')
    op.drop_column('encounters', 'status')
    op.drop_column('encounters', 'appointment_id')
    op.drop_column('encounters', 'practitioner_id')
    op.drop_column('encounters', 'practice_id')
    _drop_foreign_key_for_column("clinical_diagnoses", "practice_id")
    op.drop_index('ix_clinical_diagnoses_practice_id', table_name='clinical_diagnoses')
    op.drop_index('ix_clinical_diagnoses_patient_id', table_name='clinical_diagnoses')
    op.alter_column('clinical_diagnoses', 'patient_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('clinical_diagnoses', 'severity')
    op.drop_column('clinical_diagnoses', 'resolved_date')
    op.drop_column('clinical_diagnoses', 'onset_date')
    op.drop_column('clinical_diagnoses', 'is_active')
    op.drop_column('clinical_diagnoses', 'practice_id')
    op.drop_index('ix_result_items_result_id', table_name='result_items')
    op.drop_table('result_items')
    op.drop_index('ix_reminders_practice_id', table_name='reminders')
    op.drop_index('ix_reminders_patient_id', table_name='reminders')
    op.drop_table('reminders')
    op.drop_index('ix_results_status', table_name='results')
    op.drop_index('ix_results_practice_id', table_name='results')
    op.drop_index('ix_results_patient_id', table_name='results')
    op.drop_table('results')
    op.drop_index('ix_test_requests_patient_id', table_name='test_requests')
    op.drop_table('test_requests')
    op.drop_index('ix_referrals_patient_id', table_name='referrals')
    op.drop_table('referrals')
    op.drop_index('ix_rag_feedback_practice_id', table_name='rag_feedback')
    op.drop_table('rag_feedback')
    op.drop_index('ix_mhr_uploads_patient_id', table_name='mhr_uploads')
    op.drop_table('mhr_uploads')
    op.drop_index('ix_invoices_patient_id', table_name='invoices')
    op.drop_table('invoices')
    op.drop_index('ix_consent_forms_patient_id', table_name='consent_forms')
    op.drop_table('consent_forms')
    op.drop_index('ix_clinical_images_patient_id', table_name='clinical_images')
    op.drop_table('clinical_images')
    op.drop_index('ix_care_plans_practice_id', table_name='care_plans')
    op.drop_index('ix_care_plans_patient_id', table_name='care_plans')
    op.drop_table('care_plans')
    op.drop_index('ix_internal_messages_recipient_id', table_name='internal_messages')
    op.drop_index('ix_internal_messages_practice_id', table_name='internal_messages')
    op.drop_table('internal_messages')
    op.drop_index('ix_checkin_events_patient_id', table_name='checkin_events')
    op.drop_table('checkin_events')
    op.drop_index('ix_call_log_practice_id', table_name='call_log')
    op.drop_table('call_log')
    op.drop_index('ix_appointments_start_time', table_name='appointments')
    op.drop_index('ix_appointments_practitioner_id', table_name='appointments')
    op.drop_index('ix_appointments_practice_id', table_name='appointments')
    op.drop_index('ix_appointments_patient_id', table_name='appointments')
    op.drop_table('appointments')
    op.drop_index('ix_users_practice_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_schedule_overrides_practitioner_id_date', table_name='schedule_overrides')
    op.drop_table('schedule_overrides')
    op.drop_index('ix_scanned_documents_patient_id', table_name='scanned_documents')
    op.drop_table('scanned_documents')
    op.drop_index('ix_practitioner_schedules_practitioner_id', table_name='practitioner_schedules')
    op.drop_table('practitioner_schedules')
    op.drop_index('ix_sms_log_practice_id', table_name='sms_log')
    op.drop_index('ix_sms_log_patient_id', table_name='sms_log')
    op.drop_table('sms_log')
    op.drop_index('ix_practitioners_practice_id', table_name='practitioners')
    op.drop_table('practitioners')
    op.drop_index('ix_patient_qr_tokens_patient_id', table_name='patient_qr_tokens')
    op.drop_table('patient_qr_tokens')
    op.drop_index('ix_patient_history_patient_id', table_name='patient_history')
    op.drop_table('patient_history')
    op.drop_index('ix_immunisations_patient_id', table_name='immunisations')
    op.drop_table('immunisations')
    op.drop_index('ix_ihi_records_patient_id', table_name='ihi_records')
    op.drop_table('ihi_records')
    op.drop_index('ix_allergies_patient_id', table_name='allergies')
    op.drop_table('allergies')
    op.drop_index('ix_practice_locations_practice_id', table_name='practice_locations')
    op.drop_table('practice_locations')
    op.drop_table('community_encounters')
    op.drop_index('ix_appointment_types_practice_id', table_name='appointment_types')
    op.drop_table('appointment_types')
    op.drop_table('practices')
    # ### end Alembic commands ###
