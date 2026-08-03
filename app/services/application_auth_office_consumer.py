"""Default-off one-use lifecycle for a bounded Office read consumer.

This module owns no route, database, cookie, provider, identity, or product
authority.  A task-specific composition registers opaque launch material and
uses the returned decisions to deliver one ready page or an inert replay page.
"""

from __future__ import annotations

import hashlib
import secrets
import threading
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from app.services.application_auth_runtime import Surface


class OfficeConsumerDeliveryState(StrEnum):
    READY = "ready"
    INERT = "inert"


class OfficeConsumerLifecycleReason(StrEnum):
    DELIVERY_READY = "delivery_ready"
    DELIVERY_REPLAYED = "delivery_replayed"
    REPLAY_SESSION_REVOKED = "replay_session_revoked"
    REPLAY_SESSION_REVOCATION_FAILED = "replay_session_revocation_failed"
    PRODUCT_READ_DENIED = "product_read_denied"
    SESSION_LOSS_RECONCILED = "session_loss_reconciled"
    RESULT_NONCE_REJECTED = "result_nonce_rejected"
    RESULT_NONCE_REPLAYED = "result_nonce_replayed"
    TERMINAL_SUCCESS = "terminal_success"
    TERMINAL_FAIL = "terminal_fail"


class OfficeConsumerNonceRejected(RuntimeError):
    """A supplied result nonce did not belong to the selected surface."""


class OfficeConsumerNonceReplayed(RuntimeError):
    """A result nonce was reused after its one terminal admission."""


@dataclass(frozen=True)
class OfficeConsumerDelivery:
    state: OfficeConsumerDeliveryState
    surface: Surface
    expected_host: str
    directory_endpoint: str
    session_value: str
    csrf_value: str
    evidence_nonce: str
    revoke_session_value: str


@dataclass
class _Launch:
    session_value: str
    csrf_value: str | None
    evidence_nonce: str | None
    evidence_nonce_hash: str
    delivered: bool = False
    replay_revocation_requested: bool = False
    replay_revocation_completed: bool = False
    result_admitted: bool = False


class DefaultOffOfficeConsumerAdapter:
    """Coordinate a fixed set of one-use Office surface launches.

    The adapter deliberately returns a session value only to the owning
    composition. It never validates or revokes that value itself and cannot
    create product authority. All durable observations are fixed reason counts.
    """

    def __init__(
        self,
        *,
        expected_hosts: Mapping[Surface, str],
        directory_endpoints: Mapping[Surface, str],
    ) -> None:
        if set(expected_hosts) != set(directory_endpoints):
            raise ValueError("Office consumer surfaces must match exactly")
        if not expected_hosts:
            raise ValueError("at least one Office consumer surface is required")
        self._expected_hosts = dict(expected_hosts)
        self._directory_endpoints = dict(directory_endpoints)
        self._launches: dict[Surface, _Launch] = {}
        self._counts = {reason.value: 0 for reason in OfficeConsumerLifecycleReason}
        self._lock = threading.Lock()

    @staticmethod
    def hash_nonce(value: str) -> str:
        return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"

    def register_launch(
        self,
        *,
        surface: Surface,
        session_value: str,
        csrf_value: str,
        evidence_nonce: str,
    ) -> None:
        if surface not in self._expected_hosts:
            raise ValueError("surface is outside the fixed Office consumer set")
        if not all((session_value, csrf_value, evidence_nonce)):
            raise ValueError("opaque launch material must be non-empty")
        with self._lock:
            if surface in self._launches:
                raise ValueError("surface launch is already registered")
            self._launches[surface] = _Launch(
                session_value=session_value,
                csrf_value=csrf_value,
                evidence_nonce=evidence_nonce,
                evidence_nonce_hash=self.hash_nonce(evidence_nonce),
            )

    def deliver(self, surface: Surface) -> OfficeConsumerDelivery:
        with self._lock:
            launch = self._launches[surface]
            if not launch.delivered:
                launch.delivered = True
                csrf_value = launch.csrf_value or ""
                evidence_nonce = launch.evidence_nonce or ""
                launch.csrf_value = None
                launch.evidence_nonce = None
                self._counts[OfficeConsumerLifecycleReason.DELIVERY_READY.value] += 1
                return OfficeConsumerDelivery(
                    state=OfficeConsumerDeliveryState.READY,
                    surface=surface,
                    expected_host=self._expected_hosts[surface],
                    directory_endpoint=self._directory_endpoints[surface],
                    session_value=launch.session_value,
                    csrf_value=csrf_value,
                    evidence_nonce=evidence_nonce,
                    revoke_session_value="",
                )

            self._counts[OfficeConsumerLifecycleReason.DELIVERY_REPLAYED.value] += 1
            revoke_value = ""
            if (
                not launch.replay_revocation_requested
                and not launch.replay_revocation_completed
            ):
                launch.replay_revocation_requested = True
                revoke_value = launch.session_value
            return OfficeConsumerDelivery(
                state=OfficeConsumerDeliveryState.INERT,
                surface=surface,
                expected_host=self._expected_hosts[surface],
                directory_endpoint="",
                session_value="",
                csrf_value="",
                evidence_nonce="",
                revoke_session_value=revoke_value,
            )

    def session_value(self, surface: Surface) -> str:
        with self._lock:
            return self._launches[surface].session_value

    def complete_replay_revocation(
        self,
        *,
        surface: Surface,
        succeeded: bool,
    ) -> None:
        with self._lock:
            launch = self._launches[surface]
            if (
                not launch.replay_revocation_requested
                or launch.replay_revocation_completed
            ):
                raise ValueError("no replay revocation is pending")
            if succeeded:
                launch.replay_revocation_completed = True
                self._counts[
                    OfficeConsumerLifecycleReason.REPLAY_SESSION_REVOKED.value
                ] += 1
                return
            launch.replay_revocation_requested = False
            self._counts[
                OfficeConsumerLifecycleReason.REPLAY_SESSION_REVOCATION_FAILED.value
            ] += 1

    def admit_result_nonce(self, *, surface: Surface, supplied_nonce: str) -> None:
        supplied_hash = self.hash_nonce(supplied_nonce)
        with self._lock:
            launch = self._launches[surface]
            if not secrets.compare_digest(
                supplied_hash,
                launch.evidence_nonce_hash,
            ):
                self._counts[
                    OfficeConsumerLifecycleReason.RESULT_NONCE_REJECTED.value
                ] += 1
                raise OfficeConsumerNonceRejected("result nonce was not admitted")
            if launch.result_admitted:
                self._counts[
                    OfficeConsumerLifecycleReason.RESULT_NONCE_REPLAYED.value
                ] += 1
                raise OfficeConsumerNonceReplayed("result nonce was already consumed")
            launch.result_admitted = True

    def record_reason(self, reason: OfficeConsumerLifecycleReason) -> None:
        with self._lock:
            self._counts[reason.value] += 1

    def sanitized_snapshot(self) -> dict[str, object]:
        with self._lock:
            counts = dict(self._counts)
        return {
            "schema_version": "raisa.office_consumer_lifecycle.v1",
            "reason_counts": counts,
            "identifier_fields_present": False,
            "raw_values_present": False,
        }
