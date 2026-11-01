"""Inert trusted-server adapter for five restricted patient SQL operations.

No engine or verifier is constructed here. An explicit isolated trusted factory
must inject the owned tenant Engine and existing backend signing secret. JWT and
signer imports are lazy so pure contract tests do not read config or .env.
SQL locks and current checks, not a signature or request User, authorise writes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import re
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.schemas.patient_registration import (
    CANONICALIZATION_VERSION, CONFIRMATION_PURPOSE, ConfirmRegistration,
    PrepareRegistration, canonical_registration_body,
)


class PatientRegistrationError(RuntimeError):
    def __init__(self, status_code=403, code="PATIENT_REGISTRATION_DENIED"):
        self.status_code, self.code = status_code, code
        super().__init__(code)


def require_patient_policy(role, action):
    if (type(role) is not str or role not in ("Receptionist", "PracticeOwner")
            or action not in ("patient.read", "patient.create")):
        raise PatientRegistrationError()


@dataclass(frozen=True, repr=False)
class _Principal:
    account: UUID
    membership: UUID
    user: UUID
    practice: UUID
    role: str
    generation: int
    expiry: datetime


def _verified_principal(token):
    # Adapt the exact existing invitation verified-principal/expiry pattern.
    from app.services import auth_service
    try:
        claims = auth_service.verify_token(token)
        payload = auth_service._decode(token, auth_service.TENANT_AUDIENCE, [
            "sub", "account_id", "membership_id", "practice_id", "authority_generation", "role"])
        expiry = payload.get("exp")
        if type(expiry) is not int or not 1 <= expiry <= 253402300799:
            raise ValueError("expiry")
        expiry = datetime.fromtimestamp(expiry, timezone.utc)
        if expiry <= datetime.now(timezone.utc):
            raise ValueError("expiry")
        return _Principal(claims.account_id, claims.membership_id, claims.user_id,
                          claims.practice_id, claims.role, claims.authority_generation, expiry)
    except Exception:
        raise PatientRegistrationError(401, "PATIENT_AUTHENTICATION_REQUIRED") from None


_AUTH_ARGS = ":account,:membership,:user,:practice,:role,:generation,:expiry"


def _params(p):
    return dict(account=p.account, membership=p.membership, user=p.user,
                practice=p.practice, role=p.role, generation=p.generation, expiry=p.expiry)


def _draft_expiry(value):
    if type(value) is not str:
        raise PatientRegistrationError(409, "PATIENT_CONFIRMATION_INVALID")
    try:
        result = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        if result.strftime("%Y-%m-%dT%H:%M:%S.%fZ") != value:
            raise ValueError("noncanonical expiry")
        return result
    except ValueError:
        raise PatientRegistrationError(409, "PATIENT_CONFIRMATION_INVALID") from None


def _confirmation_payload(p, *, command_key, command_id, intent, revision, digest,
                          original_role, original_generation, expires_at):
    if (original_role not in ("Receptionist", "PracticeOwner")
            or type(original_generation) is not int or original_generation < 1):
        raise PatientRegistrationError(409, "PATIENT_CONFIRMATION_INVALID")
    _draft_expiry(expires_at)
    return {"schema_version": "patient.registration.confirmation.v1",
            "canonicalization_version": CANONICALIZATION_VERSION,
            "account_id": str(p.account), "membership_id": str(p.membership),
            "user_id": str(p.user), "practice_id": str(p.practice),
            "role": original_role, "authority_generation": original_generation,
            "registration_intent_id": str(intent), "command_id": str(command_id),
            "command_key": str(command_key), "draft_revision": revision,
            "body_digest": digest, "expires_at": expires_at}


class PatientRegistrationService:
    def __init__(self, engine, *, enabled=False, signing_secret=None,
                 expected_database=None, expected_port=None):
        from sqlalchemy.engine import Engine
        from sqlalchemy.pool import NullPool
        if (enabled is not True or not isinstance(engine, Engine)
                or not isinstance(engine.pool, NullPool) or engine.echo
                or engine.hide_parameters is not True
                or engine.url.get_backend_name() != "postgresql"
                or engine.url.username != "raisa_local_tenant"
                or engine.url.host != "127.0.0.1" or bool(engine.url.query)
                or type(expected_port) is not int or not 1 <= expected_port <= 65535
                or engine.url.port != expected_port
                or type(expected_database) is not str or not expected_database
                or engine.url.database != expected_database
                or type(signing_secret) is not str or len(signing_secret) < 32):
            raise PatientRegistrationError()
        self._engine, self._secret = engine, signing_secret
        self._database, self._port = expected_database, expected_port

    def _call(self, p, function, suffix, params):
        # Function names/suffixes below are source literals, never HTTP input.
        try:
            with self._engine.begin() as connection:
                if tuple(connection.execute(text(
                        "SELECT session_user,current_user,current_database()"
                )).one()) != ("raisa_local_tenant", "raisa_local_tenant", self._database):
                    raise PatientRegistrationError()
                if connection.execute(text("SHOW transaction_isolation")).scalar_one() != "read committed":
                    raise PatientRegistrationError()
                connection.execute(text("SET LOCAL statement_timeout='8000ms'"))
                connection.execute(text("SET LOCAL lock_timeout='3000ms'"))
                value = connection.execute(text("SELECT patient_api." + function + "("
                    + _AUTH_ARGS + suffix + ")"), {**_params(p), **params}).scalar_one()
            return value  # Return only after the owned transaction committed.
        except DBAPIError as exc:
            code = getattr(exc.orig, "sqlstate", None) or getattr(exc.orig, "pgcode", None)
            if code == "42501":
                raise PatientRegistrationError() from None
            if code == "P0002":
                raise PatientRegistrationError(404, "PATIENT_NOT_FOUND") from None
            if code in ("P0001", "23505"):
                raise PatientRegistrationError(409, "PATIENT_REGISTRATION_CONFLICT") from None
            if code == "22023":
                raise PatientRegistrationError(400, "PATIENT_REGISTRATION_INVALID") from None
            # No continuation inside an aborted transaction or blind retry.
            raise PatientRegistrationError(503, "PATIENT_REGISTRATION_UNAVAILABLE") from None

    def search(self, token, query=None, date_of_birth=None, limit=10):
        p = _verified_principal(token); require_patient_policy(p.role, "patient.read")
        if query is not None:
            if type(query) is not str:
                raise PatientRegistrationError(400, "PATIENT_SEARCH_INVALID")
            query = query.strip() or None
        if (query is not None and not 2 <= len(query) <= 100
                or date_of_birth is not None and (type(date_of_birth) is not date
                    or date_of_birth > datetime.now(timezone.utc).date())
                or query is None and date_of_birth is None
                or type(limit) is not int or not 1 <= limit <= 20):
            raise PatientRegistrationError(400, "PATIENT_SEARCH_INVALID")
        return self._call(p, "patient_search", ",:query,:dob,:limit",
                          dict(query=query, dob=date_of_birth, limit=limit))

    def read(self, token, patient_id):
        p = _verified_principal(token); require_patient_policy(p.role, "patient.read")
        if type(patient_id) is not UUID:
            raise PatientRegistrationError(400, "PATIENT_ID_INVALID")
        return self._call(p, "patient_read", ",:patient", dict(patient=patient_id))

    def prepare(self, token, request: PrepareRegistration):
        p = _verified_principal(token); require_patient_policy(p.role, "patient.create")
        if type(request) is not PrepareRegistration:
            raise PatientRegistrationError(400, "PATIENT_REGISTRATION_INVALID")
        body, canonical, digest = canonical_registration_body(request.body)
        result = self._call(p, "registration_prepare",
            ",:key,:first,:last,:dob,:distinct,:canonical,:digest,:new,:intent,:predecessor,:revision",
            dict(key=request.command_key, first=body["first_name"], last=body["last_name"],
                 dob=request.body.date_of_birth, distinct=request.body.distinct_person,
                 canonical=canonical, digest=digest, new=request.new_registration,
                 intent=request.registration_intent_id, predecessor=request.supersedes_command_id,
                 revision=request.supersedes_revision))
        if result["state"] == "committed":
            return result
        draft = result["draft"]
        if draft["requires_distinct_person_decision"]:
            return {**result, "confirmation_evidence": None}
        from app.services.bernie_turn_evidence import mint_signed_confirmation_evidence
        payload = _confirmation_payload(p, command_key=draft["command_key"],
            command_id=draft["command_id"], intent=draft["registration_intent_id"],
            revision=draft["draft_revision"], digest=draft["body_digest"],
            original_role=draft["role"], original_generation=draft["authority_generation"],
            expires_at=draft["expires_at"])
        return {**result, "confirmation_evidence": mint_signed_confirmation_evidence(
            payload, evidence_purpose=CONFIRMATION_PURPOSE, secret=self._secret)}

    def confirm(self, token, request: ConfirmRegistration):
        p = _verified_principal(token); require_patient_policy(p.role, "patient.create")
        if type(request) is not ConfirmRegistration:
            raise PatientRegistrationError(400, "PATIENT_CONFIRMATION_INVALID")
        original = request.signed_confirmation_evidence.get("payload")
        if type(original) is not dict:
            raise PatientRegistrationError(409, "PATIENT_CONFIRMATION_INVALID")
        payload = _confirmation_payload(p, command_key=request.command_key,
            command_id=request.command_id, intent=request.registration_intent_id,
            revision=request.draft_revision, digest=request.body_digest,
            original_role=original.get("role"), original_generation=original.get("authority_generation"),
            expires_at=original.get("expires_at"))
        # Generic equality treats True as 1. Require exact primitive types too;
        # cryptographic verification remains solely in the unchanged signer.
        if (original.keys() != payload.keys()
                or any(type(original[k]) is not type(v) or original[k] != v for k, v in payload.items())):
            raise PatientRegistrationError(409, "PATIENT_CONFIRMATION_INVALID")
        from app.services.bernie_turn_evidence import verify_signed_confirmation_evidence
        checked = verify_signed_confirmation_evidence(request.signed_confirmation_evidence,
            payload, expected_purpose=CONFIRMATION_PURPOSE, secret=self._secret)
        if checked.verified is not True:
            raise PatientRegistrationError(409, "PATIENT_CONFIRMATION_INVALID")
        return self._call(p, "registration_confirm",
            ",:key,:command,:intent,:revision,:digest,:original_role,:original_generation,:draft_expiry,:confirmed",
            dict(key=request.command_key, command=request.command_id,
                 intent=request.registration_intent_id, revision=request.draft_revision,
                 digest=request.body_digest, original_role=payload["role"],
                 original_generation=payload["authority_generation"],
                 draft_expiry=_draft_expiry(payload["expires_at"]), confirmed=request.confirmed))

    def receipt(self, token, command_key):
        p = _verified_principal(token); require_patient_policy(p.role, "patient.read")
        if type(command_key) is not UUID:
            raise PatientRegistrationError(400, "PATIENT_COMMAND_KEY_INVALID")
        return self._call(p, "registration_receipt", ",:key", dict(key=command_key))
