"""STOPPED candidate: trusted adapter for three restricted CREATE operations.

The factory, protected connection and verified HTTP path are trusted boundaries.
SQL parameters, GUCs, signatures and row locks do not authenticate hostile SQL.
No Engine, credential, principal verifier or signing-key source is created here.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.schemas.practitioner_create_command import (
    CANONICALIZATION_VERSION, CONFIRMATION_PURPOSE, CONFIRMATION_SCHEMA,
    EVIDENCE_VERSION, ConfirmPractitionerCreate, PreparePractitionerCreate,
    canonical_practitioner_body,
)


class PractitionerCreateError(RuntimeError):
    def __init__(self, status_code=403, code="PRACTITIONER_CREATE_DENIED"):
        self.status_code, self.code = status_code, code
        super().__init__(code)


def _principal(token):
    # Reuse the existing verified token/UTC expiry adapter, not patient policy.
    from app.services.patient_registration import PatientRegistrationError, _verified_principal
    try:
        p = _verified_principal(token)
    except PatientRegistrationError:
        raise PractitionerCreateError(401, "PRACTITIONER_AUTHENTICATION_REQUIRED") from None
    if (any(type(v) is not UUID for v in (p.account, p.membership, p.user, p.practice))
            or type(p.role) is not str or p.role != "PracticeOwner"
            or type(p.generation) is not int or p.generation < 1
            or type(p.expiry) is not datetime or p.expiry.tzinfo is not timezone.utc
            or p.expiry <= datetime.now(timezone.utc)):
        raise PractitionerCreateError()
    return p


def _draft_expiry(value):
    if type(value) is not str:
        raise PractitionerCreateError(409, "PRACTITIONER_CONFIRMATION_INVALID")
    try:
        expiry = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        if expiry.strftime("%Y-%m-%dT%H:%M:%S.%fZ") != value:
            raise ValueError("noncanonical expiry")
        return expiry
    except ValueError:
        raise PractitionerCreateError(409, "PRACTITIONER_CONFIRMATION_INVALID") from None


def _payload(p, *, command_key, command_id, intent, revision, body_digest,
             matching_digest, original_role, original_generation, expires_at):
    if (type(original_role) is not str or original_role != "PracticeOwner"
            or type(original_generation) is not int or original_generation < 1
            or type(revision) is not int or revision < 1
            or any(type(v) is not str or re.fullmatch(r"[0-9a-f]{64}", v) is None
                   for v in (body_digest, matching_digest))):
        raise PractitionerCreateError(409, "PRACTITIONER_CONFIRMATION_INVALID")
    _draft_expiry(expires_at)
    return {"schema_version": CONFIRMATION_SCHEMA,
            "canonicalization_version": CANONICALIZATION_VERSION,
            "account_id": str(p.account), "membership_id": str(p.membership),
            "user_id": str(p.user), "practice_id": str(p.practice),
            "role": original_role, "authority_generation": original_generation,
            "command_id": str(command_id), "command_key": str(command_key),
            "create_intent_id": str(intent), "draft_revision": revision,
            "body_digest": body_digest, "matching_context_digest": matching_digest,
            "expires_at": expires_at}


_AUTH = ":account,:membership,:user,:practice,:role,:generation,:expiry"
# Operation choice and parameter names are literals, never request identifiers.
_SQL = {
    "prepare": "SELECT practitioner_api.prepare_create(" + _AUTH
        + ",:key,:first,:last,:specialty,:distinct,:canonical,:digest,:new,:intent,:predecessor,:revision)",
    "confirm": "SELECT practitioner_api.confirm_create(" + _AUTH
        + ",:key,:command,:intent,:revision,:digest,:matching,:original_role,:original_generation,:draft_expiry,:confirmed)",
    "receipt": "SELECT practitioner_api.read_create_receipt(" + _AUTH + ",:key)",
}


class PractitionerCreateService:
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
            raise PractitionerCreateError()
        self._engine, self._secret = engine, signing_secret
        self._database = expected_database

    def _call(self, p, operation, params):
        try:
            with self._engine.begin() as connection:
                if tuple(connection.execute(text(
                        "SELECT session_user,current_user,current_database()"
                )).one()) != ("raisa_local_tenant", "raisa_local_tenant", self._database):
                    raise PractitionerCreateError()
                if connection.execute(text("SHOW transaction_isolation")).scalar_one() != "read committed":
                    raise PractitionerCreateError()
                connection.execute(text("SET LOCAL statement_timeout='8000ms'"))
                connection.execute(text("SET LOCAL lock_timeout='3000ms'"))
                value = connection.execute(text(_SQL[operation]), {
                    "account": p.account, "membership": p.membership, "user": p.user,
                    "practice": p.practice, "role": p.role, "generation": p.generation,
                    "expiry": p.expiry, **params,
                }).scalar_one()
            return value  # No receipt/result escapes before commit succeeds.
        except DBAPIError as exc:
            code = getattr(exc.orig, "sqlstate", None) or getattr(exc.orig, "pgcode", None)
            if code == "42501":
                raise PractitionerCreateError() from None
            if code == "P0002":
                raise PractitionerCreateError(404, "PRACTITIONER_CREATE_NOT_FOUND") from None
            if code in ("P0001", "23505", "40001", "40P01", "55P03", "57014"):
                raise PractitionerCreateError(409, "PRACTITIONER_CREATE_CONFLICT") from None
            if code == "22023":
                raise PractitionerCreateError(400, "PRACTITIONER_CREATE_INVALID") from None
            raise PractitionerCreateError(503, "PRACTITIONER_CREATE_UNAVAILABLE") from None

    def prepare(self, token, request: PreparePractitionerCreate):
        p = _principal(token)
        if type(request) is not PreparePractitionerCreate:
            raise PractitionerCreateError(400, "PRACTITIONER_CREATE_INVALID")
        body, canonical, digest = canonical_practitioner_body(request.body)
        result = self._call(p, "prepare", {
            "key": request.command_key, "first": body["first_name"],
            "last": body["last_name"], "specialty": body["specialty"],
            "distinct": body["distinct_resource"], "canonical": canonical,
            "digest": digest, "new": request.new_intent, "intent": request.create_intent_id,
            "predecessor": request.supersedes_command_id, "revision": request.supersedes_revision,
        })
        if result["state"] == "committed":
            return result
        draft = result["draft"]
        if draft["requires_distinct_resource_decision"]:
            return {**result, "confirmation_evidence": None}
        payload = _payload(p, command_key=draft["command_key"], command_id=draft["command_id"],
            intent=draft["create_intent_id"], revision=draft["draft_revision"],
            body_digest=draft["body_digest"], matching_digest=draft["matching_context_digest"],
            original_role=draft["role"], original_generation=draft["authority_generation"],
            expires_at=draft["expires_at"])
        if datetime.now(timezone.utc) >= min(p.expiry, _draft_expiry(draft["expires_at"])):
            raise PractitionerCreateError(409, "PRACTITIONER_CREATE_CONFLICT")
        from app.services.bernie_turn_evidence import mint_signed_confirmation_evidence
        return {**result, "confirmation_evidence": mint_signed_confirmation_evidence(
            payload, evidence_purpose=CONFIRMATION_PURPOSE, secret=self._secret)}

    def confirm(self, token, request: ConfirmPractitionerCreate):
        p = _principal(token)
        if type(request) is not ConfirmPractitionerCreate or request.confirmed is not True:
            raise PractitionerCreateError(400, "PRACTITIONER_CONFIRMATION_INVALID")
        envelope = request.signed_confirmation_evidence
        if (type(envelope) is not dict or set(envelope) != {"schema_version", "purpose", "payload", "signature"}
                or type(envelope["schema_version"]) is not str or envelope["schema_version"] != EVIDENCE_VERSION
                or type(envelope["purpose"]) is not str or envelope["purpose"] != CONFIRMATION_PURPOSE
                or type(envelope["signature"]) is not str
                or re.fullmatch(r"[0-9a-f]{64}", envelope["signature"]) is None
                or type(envelope["payload"]) is not dict):
            raise PractitionerCreateError(409, "PRACTITIONER_CONFIRMATION_INVALID")
        original = envelope["payload"]
        payload = _payload(p, command_key=request.command_key, command_id=request.command_id,
            intent=request.create_intent_id, revision=request.draft_revision,
            body_digest=request.body_digest, matching_digest=request.matching_context_digest,
            original_role=original.get("role"), original_generation=original.get("authority_generation"),
            expires_at=original.get("expires_at"))
        if (original.keys() != payload.keys()
                or any(type(original[k]) is not type(v) or original[k] != v for k, v in payload.items())):
            raise PractitionerCreateError(409, "PRACTITIONER_CONFIRMATION_INVALID")
        from app.services.bernie_turn_evidence import verify_signed_confirmation_evidence
        checked = verify_signed_confirmation_evidence(envelope, payload,
            expected_purpose=CONFIRMATION_PURPOSE, secret=self._secret)
        if checked.verified is not True:
            raise PractitionerCreateError(409, "PRACTITIONER_CONFIRMATION_INVALID")
        # Fresh principal generation and historical proposal generation remain
        # separate: SQL accepts the latter after expiry only for exact commit replay.
        return self._call(p, "confirm", {
            "key": request.command_key, "command": request.command_id,
            "intent": request.create_intent_id, "revision": request.draft_revision,
            "digest": request.body_digest, "matching": request.matching_context_digest,
            "original_role": payload["role"], "original_generation": payload["authority_generation"],
            "draft_expiry": _draft_expiry(payload["expires_at"]), "confirmed": request.confirmed,
        })

    def receipt(self, token, command_key):
        p = _principal(token)
        if type(command_key) is not UUID:
            raise PractitionerCreateError(400, "PRACTITIONER_COMMAND_KEY_INVALID")
        return self._call(p, "receipt", {"key": command_key})
