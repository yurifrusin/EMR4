"""
All protected endpoints must reject requests without a valid Bearer token.
These tests verify the authentication gate without exercising AI or DB logic.
"""

import pytest

ENDPOINTS = [
    ("GET",  "/api/v1/appointments"),
    ("GET",  "/api/v1/appointments/types"),
    ("POST", "/api/v1/analyze-consultation"),
    ("POST", "/api/v1/finalize"),
]


@pytest.mark.parametrize("method,path", ENDPOINTS)
def test_unauthenticated_returns_401(client, method, path):
    resp = getattr(client, method.lower())(path)
    assert resp.status_code == 401, (
        f"{method} {path} returned {resp.status_code}, expected 401"
    )


def test_invalid_token_returns_401(client):
    resp = client.get(
        "/api/v1/appointments",
        headers={"Authorization": "Bearer not.a.valid.token"},
    )
    assert resp.status_code == 401


def test_valid_token_reaches_endpoint(client, gp_user):
    """Sanity-check: a valid token is accepted (even if response is empty list)."""
    from tests.conftest import make_token
    token = make_token(gp_user)
    resp = client.get(
        "/api/v1/appointments",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
