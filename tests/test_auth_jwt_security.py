"""Focused security contract for EMR4 JWT authentication."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.config import Settings, settings
from app.services.auth_service import create_access_token, verify_token


def _claims() -> dict[str, str]:
    return {
        "sub": str(uuid4()),
        "practice_id": str(uuid4()),
        "role": "Receptionist",
    }


def test_hs256_token_round_trip_preserves_scoped_identity() -> None:
    claims = _claims()
    token = create_access_token(claims)
    decoded = verify_token(token)
    assert str(decoded.user_id) == claims["sub"]
    assert str(decoded.practice_id) == claims["practice_id"]
    assert decoded.role == claims["role"]


def test_invalid_and_expired_tokens_fail_closed() -> None:
    with pytest.raises(HTTPException) as invalid:
        verify_token("not-a-jwt")
    assert invalid.value.status_code == 401

    expired = create_access_token(_claims(), expires_delta=timedelta(seconds=-1))
    with pytest.raises(HTTPException) as expired_error:
        verify_token(expired)
    assert expired_error.value.status_code == 401


def test_algorithm_confusion_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    signing_key = "k" * 64
    monkeypatch.setattr(settings, "secret_key", signing_key)
    token = jwt.encode(_claims(), signing_key, algorithm="HS512")
    with pytest.raises(HTTPException) as error:
        verify_token(token)
    assert error.value.status_code == 401


def test_configuration_rejects_unreviewed_jwt_algorithms() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, algorithm="ES256")


def test_requirements_remove_python_jose_and_transitive_ecdsa() -> None:
    requirements = (
        Path(__file__).resolve().parents[1] / "requirements.txt"
    ).read_text(encoding="utf-8")
    assert "PyJWT==2.13.0" in requirements
    assert "python-jose" not in requirements
    assert "ecdsa" not in requirements
