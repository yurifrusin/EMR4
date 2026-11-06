"""Ephemeral HS256 JWT codec for the synthetic local organisation mock.

The qualified entry puts the pinned PyJWT vendor directory on its import path
before importing this module. Keys exist only in this process and are never
serialized. This is not a PRODA protocol or identity-verification adapter.
"""

from __future__ import annotations

import secrets
from typing import Mapping

import jwt

from mock_auth import AUDIENCE, ISSUER, AuthDenied


_CLAIMS = frozenset({"iss", "aud", "mock", "sub", "org", "scope",
                     "iat", "nbf", "exp", "jti"})
_HEADER = {"alg": "HS256", "typ": "JWT"}
_MAX_TOKEN_BYTES = 4096


class LocalHS256Jwt:
    """One process-local signing key; verification admits HS256 only."""

    __slots__ = ("_key",)

    def __init__(self) -> None:
        self._key = secrets.token_bytes(32)

    def __repr__(self) -> str:
        return "LocalHS256Jwt(<ephemeral-key-redacted>)"

    def issue(self, claims: Mapping[str, object]) -> str:
        if (type(claims) is not dict or set(claims) != _CLAIMS
                or claims["iss"] != ISSUER or claims["aud"] != AUDIENCE
                or claims["mock"] is not True
                or any(type(claims[name]) is not str
                       for name in ("sub", "org", "scope", "jti"))
                or any(type(claims[name]) is not int
                       for name in ("iat", "nbf", "exp"))):
            raise AuthDenied("TOKEN_ISSUE_FAILED")
        try:
            token = jwt.encode(dict(claims), self._key, algorithm="HS256",
                               headers=_HEADER)
        except (jwt.PyJWTError, ValueError, TypeError) as exc:
            raise AuthDenied("TOKEN_ISSUE_FAILED") from exc
        if (type(token) is not str or not token.isascii()
                or len(token.encode("ascii")) > _MAX_TOKEN_BYTES):
            raise AuthDenied("TOKEN_ISSUE_FAILED")
        return token

    def verify(self, token: str) -> dict[str, object]:
        if (type(token) is not str or not token.isascii()
                or len(token) > _MAX_TOKEN_BYTES or token.count(".") != 2):
            raise AuthDenied("TOKEN_INVALID")
        try:
            header = jwt.get_unverified_header(token)
            if type(header) is not dict or header != _HEADER:
                raise AuthDenied("TOKEN_INVALID")
            claims = jwt.decode(
                token, self._key, algorithms=["HS256"],
                audience=AUDIENCE, issuer=ISSUER,
                options={"require": list(_CLAIMS),
                         "verify_signature": True,
                         "verify_aud": True, "verify_iss": True,
                         # MockOrgAuth uses its server clock and checks the
                         # current member/delegation ledger each operation.
                         "verify_exp": False, "verify_nbf": False,
                         "verify_iat": False})
        except (jwt.PyJWTError, ValueError, TypeError) as exc:
            raise AuthDenied("TOKEN_INVALID") from exc
        if type(claims) is not dict or set(claims) != _CLAIMS:
            raise AuthDenied("TOKEN_INVALID")
        return claims
