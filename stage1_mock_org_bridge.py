"""Trusted synthetic staff binding for the isolated Stage 1 demo bridge.

The local harness owns construction and token issuance. Browser input cannot
select the principal, organisation, practice, backend actor, role or scopes.
This is an additional current-state gate, never appointment-write authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from mock_auth import AuthDenied, LocalJwtCodec, MockOrgAuth


class StaffMockDenied(ValueError):
    """Fixed public denial; do not expose token or ledger details."""


@dataclass(frozen=True, repr=False)
class StaffMockBinding:
    authority: MockOrgAuth = field(repr=False)
    codec: LocalJwtCodec = field(repr=False)
    token: str = field(repr=False)
    user_id: str
    org_id: str
    practice_id: str
    staff_user_id: str
    display_label: str

    def __post_init__(self) -> None:
        if (not all(type(v) is str and v for v in (
                self.token, self.user_id, self.org_id, self.practice_id,
                self.staff_user_id, self.display_label))
                or len(self.display_label) > 80):
            raise ValueError("MOCK_STAFF_BINDING_INVALID")

    def require(self, *, practice_id: str, staff_user_id: str,
                scope: str = "demo:use", token: str | None = None) -> None:
        if (practice_id != self.practice_id or
                staff_user_id != self.staff_user_id):
            raise StaffMockDenied("MOCK_STAFF_UNAVAILABLE")
        try:
            grant = self.authority.authorize(
                self.token if token is None else token,
                org_id=self.org_id, required_scope=scope,
                codec=self.codec)
        except AuthDenied as exc:
            raise StaffMockDenied("MOCK_STAFF_UNAVAILABLE") from exc
        if (grant.user_id != self.user_id or grant.org_id != self.org_id
                or grant.granted_scope != scope or grant.mock is not True):
            raise StaffMockDenied("MOCK_STAFF_UNAVAILABLE")

    def expiry_for(self, token: str) -> datetime:
        self.require(practice_id=self.practice_id, staff_user_id=self.staff_user_id,
                     token=token)
        try:
            claims = self.codec.verify(token)
            exp = claims["exp"]
            if type(exp) is not int:
                raise ValueError("EXP_INVALID")
            return datetime.fromtimestamp(exp, timezone.utc)
        except Exception as exc:
            raise StaffMockDenied("MOCK_STAFF_UNAVAILABLE") from exc

    def issue_current(self) -> tuple[str, datetime]:
        """Explicit trusted continuation for the same synthetic fixture only."""
        try:
            token = self.authority.issue(selected_user_id=self.user_id,
                org_id=self.org_id, scopes=("demo:use", "proposal:create"),
                codec=self.codec)
            self.require(practice_id=self.practice_id,
                staff_user_id=self.staff_user_id, scope="proposal:create",
                token=token)
            return token, self.expiry_for(token)
        except AuthDenied as exc:
            raise StaffMockDenied("MOCK_STAFF_UNAVAILABLE") from exc

    def projected_identity(self) -> dict[str, str | bool]:
        return {"mode": "synthetic_mock", "mock": True,
                "user_label": self.display_label,
                "practice_label": self.practice_id,
                "status": "active"}
