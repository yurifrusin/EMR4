"""Production-profile containment regression tests (G2; source candidate).

Candidate tests for the G2 production-profile repair, covering
EXACTLY the reviewed V2 test designs:

- ``production-profile-config-design-v2.md`` ("Exact configuration contract"
  and the ``tests/test_production_profile.py`` focused test scope);
- ``production-profile-scope-draft-v2.md`` ("Exact proposed behavior" 1-7 and
  "Verification corrections and acceptance");
- acceptance families CFG/SRV/AUTH/SAFE from
  ``production-profile-acceptance-cases.json``. BROW families are later-only
  and are NOT implemented here.

Isolation contract (no ``tests.conftest`` or
``tests/test_bernie_dev_fixtures.py`` import anywhere in this file):

- This module never imports ``app.*`` at top level. Every settings or
  application build installs a closed literal process environment (an exact
  ``dict`` of case variables; nothing inherited) AND an empty working
  directory BEFORE the first relevant import, evicts all ``app.*`` modules,
  and only then imports ``app.config``/``app.main``. The same boundary stays
  active through lifespan startup, requests, shutdown and module restoration.
  ``Settings(_env_file=None)`` alone is NOT treated as isolation. The reviewed
  runner must provide a literal process envelope before collection.
- Each serving case issues actual ASGI requests through ``TestClient``
  against a separately constructed dev/staging/production application.
  Route-table inspection is supporting evidence only, never the oracle.
- Stubbed-identity smoke coverage is separately labelled. The mandatory
  password/JWT/current-user positive requires the external reviewed
  ``production_profile_runtime`` fixture with a disposable synthetic
  PostgreSQL database; a missing fixture is a hard error, never a skip.

Status: source-only candidate. No test execution or acceptance is claimed.
"""

import importlib
import json
import os
import shutil
import socket
import sys
import tempfile
import uuid
from collections.abc import Mapping
from contextlib import ExitStack, contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import text as sql_text
from sqlalchemy.engine import make_url


ROOT = Path(__file__).resolve().parents[1]
TASKPANE_DIR = ROOT / "EMR4 Sidebar" / "src" / "taskpane"
TASKPANE_CHILD_NAME = "taskpane.html"
TASKPANE_CHILD_URL = f"/taskpane/{TASKPANE_CHILD_NAME}"

# Authored synthetic credential for closed-environment builds. Never a host
# value; never read from the ambient process environment.
STRONG_TEST_SECRET = "authored-synthetic-strong-test-secret-v1"
DENIED_DATABASE_URL = "postgresql://denied:denied@127.0.0.1:1/g2_profile_denied"
# Literal pinned fact: app.config.INSECURE_DEFAULT_SECRET. Kept literal so
# this module never imports app.* outside the closed import boundary.
PUBLIC_DEFAULT_SECRET = "change-me-in-production"

DEV_DEFAULT_ORIGINS = [
    "https://yurifrusin.github.io",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
NONDEV_PROFILES = ("staging", "production")
ALL_PROFILES = ("dev", "staging", "production")

# Exact Bernie development-fixture routes (app/routers/bernie_dev.py):
# prefix /api/v1/appointments/dev + the two declared GET paths.
BERNIE_DEV_FIXTURE_PATHS = (
    "/api/v1/appointments/dev/bernie-review-fixtures",
    "/api/v1/appointments/dev/h15-read-only-explanation-preview",
)
INTERACTIVE_DOC_PATHS = ("/docs", "/redoc", "/docs/oauth2-redirect")
MEANINGFUL_ME_URL = "/api/v1/auth/me"

# Isolated stubbed-identity principal (authored synthetic UUIDs; see
# isolated_stubbed_identity). NOT a database or real-auth claim.
STUB_USER_ID = uuid.UUID("00000000-0000-4000-8000-0000000000a1")
STUB_PRACTICE_ID = uuid.UUID("00000000-0000-4000-8000-0000000000b2")
STUB_EMAIL = "synthetic-receptionist@example.invalid"
STUB_ROLE = "Receptionist"


class _Omitted:
    __slots__ = ()

    def __repr__(self):  # pragma: no cover - debugging aid
        return "<omitted>"


OMITTED = _Omitted()


# ---------------------------------------------------------------------------
# Closed settings-source boundary.
# ---------------------------------------------------------------------------

def _evict_app_modules():
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]


@contextmanager
def _closed_import_boundary(literal_env):
    """Install exact literal settings sources before the first app import.

    Replaces the inherited process environment with exactly ``literal_env``
    and moves to a fresh empty working directory so a CWD-relative ``.env``
    cannot contribute values either. Restores both afterwards. No host
    secret or host setting can leak into the enclosed import/construction.
    """
    saved_env = dict(os.environ)
    saved_cwd = os.getcwd()
    saved_app_modules = {
        name: module for name, module in sys.modules.items()
        if name == "app" or name.startswith("app.")
    }
    empty_cwd = tempfile.mkdtemp(prefix="g2-production-profile-closed-")
    try:
        os.environ.clear()
        os.environ.update(literal_env)
        os.chdir(empty_cwd)
        _evict_app_modules()
        yield
    finally:
        os.chdir(saved_cwd)
        _evict_app_modules()
        sys.modules.update(saved_app_modules)
        os.environ.clear()
        os.environ.update(saved_env)
        shutil.rmtree(empty_cwd, ignore_errors=True)


def build_settings_from_kwargs(**kwargs):
    """Construct actual Settings from explicit kwargs under a closed source."""
    kwargs["_env_file"] = None
    with _closed_import_boundary({}):
        config = importlib.import_module("app.config")
        return config.Settings(**kwargs)


def build_settings_from_env(literal_env, **kwargs):
    """Construct actual Settings from an exact literal environment mapping."""
    kwargs["_env_file"] = None
    with _closed_import_boundary(dict(literal_env)):
        config = importlib.import_module("app.config")
        return config.Settings(**kwargs)


def build_profile_app(*, environment, cors_origins=OMITTED,
                      secret_key=STRONG_TEST_SECRET, database_url=DENIED_DATABASE_URL):
    """Describe one fresh app case; construction occurs inside _client_for."""
    return SimpleNamespace(environment=environment, cors_origins=cors_origins,
                           secret_key=secret_key, database_url=database_url,
                           app=None, settings=None, database_engine=None,
                           get_current_user=None, get_db=None, db_accesses=0)


@contextmanager
def _client_for(built):
    """Keep literal sources and module identity stable through ASGI teardown.

    The reviewed runner must also disable repository conftest/plugins and
    enforce its process/network binding before collection. This local guard
    denies surprise database/provider connections in the smoke cases.
    """
    literal = {"ENVIRONMENT": built.environment, "SECRET_KEY": built.secret_key,
               "DATABASE_URL": built.database_url}
    if built.cors_origins is not OMITTED:
        literal["CORS_ORIGINS"] = json.dumps(built.cors_origins)

    def deny_db(engine):
        built.db_accesses += 1
        raise AssertionError("unreviewed database access from profile smoke test")

    def deny_network(*args, **kwargs):
        raise AssertionError("network access from profile smoke test")

    with _closed_import_boundary(literal):
        with ExitStack() as guards:
            if built.database_url == DENIED_DATABASE_URL:
                guards.enter_context(patch("sqlalchemy.engine.base.Engine.connect", deny_db))
                guards.enter_context(patch("sqlalchemy.engine.base.Engine.raw_connection", deny_db))
                guards.enter_context(patch("sqlalchemy.pool.base.Pool.connect", deny_db))
                guards.enter_context(patch.object(socket.socket, "connect", deny_network))
                guards.enter_context(patch.object(socket.socket, "connect_ex", deny_network))
                guards.enter_context(patch.object(socket, "create_connection", deny_network))
            main = importlib.import_module("app.main")
            dependencies = importlib.import_module("app.dependencies")
            built.app = main.app
            built.settings = main.settings
            built.get_current_user = dependencies.get_current_user
            built.get_db = dependencies.get_db
            built.database_engine = importlib.import_module("app.database").engine
            try:
                with TestClient(built.app, follow_redirects=False) as client:
                    yield client
            finally:
                built.app.dependency_overrides.clear()


@contextmanager
def isolated_stubbed_identity(built):
    """Isolated STUBBED-identity boundary (NOT a database/real-auth claim).

    Overrides ``get_current_user`` on this app instance only, returning an
    authored synthetic principal with fixed practice/user/role meaning. This
    proves the authenticated route is retained and the auth dependency is
    wired; it must not be read as database isolation or real-password/JWT
    verification. The separate real-auth case does not use this hook.
    """
    principal = SimpleNamespace(
        id=STUB_USER_ID,
        email=STUB_EMAIL,
        role=SimpleNamespace(value=STUB_ROLE),
        practice_id=STUB_PRACTICE_ID,
    )

    def _stubbed_user():
        return principal

    built.app.dependency_overrides[built.get_current_user] = _stubbed_user
    try:
        yield principal
    finally:
        built.app.dependency_overrides.pop(built.get_current_user, None)


def _assert_not_served_without_redirect(response):
    assert response.status_code == 404, response.status_code
    assert response.history == []
    assert "location" not in response.headers


def _assert_invalid_auth_has_no_db_access(response, built):
    assert response.status_code == 401
    assert built.db_accesses == 0, "invalid authentication attempted database access"


nondev_cors_input = pytest.mark.parametrize(
    "cors_origins", [OMITTED, []], ids=["cors-omitted", "cors-explicit-empty"]
)


def test_literal_environment_and_app_modules_span_request_then_restore():
    before_modules = {
        name: module for name, module in sys.modules.items()
        if name == "app" or name.startswith("app.")
    }
    before_keys = set(os.environ)
    before_cwd = os.getcwd()
    for profile in ("dev", "production"):
        built = build_profile_app(environment=profile)
        with _client_for(built) as client:
            assert dict(os.environ) == {
                "ENVIRONMENT": profile, "SECRET_KEY": STRONG_TEST_SECRET,
                "DATABASE_URL": DENIED_DATABASE_URL,
            }
            assert built.settings.environment == profile
            assert client.get("/health").status_code == 200
            assert built.db_accesses == 0
        assert set(os.environ) == before_keys
        assert os.getcwd() == before_cwd
        assert {
            name: module for name, module in sys.modules.items()
            if name == "app" or name.startswith("app.")
        } == before_modules


# ---------------------------------------------------------------------------
# Configuration: profile canonicalization and rejection (CFG-01).
# ---------------------------------------------------------------------------

class TestProfileCanonicalization:
    @pytest.mark.parametrize(
        ("given", "expected"),
        [
            ("dev", "dev"),
            ("DEV", "dev"),
            ("Dev", "dev"),
            ("  dev  ", "dev"),
            ("staging", "staging"),
            (" staging ", "staging"),
            ("STAGING", "staging"),
            ("Staging", "staging"),
            ("production", "production"),
            ("Production", "production"),
            ("PRODUCTION", "production"),
            ("  PRODUCTION  ", "production"),
        ],
    )
    def test_supported_spellings_canonicalize_via_env(self, given, expected):
        settings = build_settings_from_env(
            {"ENVIRONMENT": given, "SECRET_KEY": STRONG_TEST_SECRET}
        )
        assert settings.environment == expected

    @pytest.mark.parametrize(
        ("given", "expected"),
        [("DEV", "dev"), (" staging ", "staging"), ("Production", "production")],
    )
    def test_supported_spellings_canonicalize_via_kwarg(self, given, expected):
        settings = build_settings_from_kwargs(
            environment=given, secret_key=STRONG_TEST_SECRET
        )
        assert settings.environment == expected

    @pytest.mark.parametrize(
        "given",
        ["", "   ", "\t", "prod", "development", "test", "preview", "local",
         "stagging", "production2", "dev,staging", "null", "none"],
    )
    def test_blank_and_unknown_profiles_rejected_via_env(self, given):
        with pytest.raises(ValidationError):
            build_settings_from_env(
                {"ENVIRONMENT": given, "SECRET_KEY": STRONG_TEST_SECRET}
            )

    @pytest.mark.parametrize(
        "given", ["", "   ", "prod", "development", "unknown"]
    )
    def test_blank_and_unknown_profiles_rejected_via_kwarg(self, given):
        with pytest.raises(ValidationError):
            build_settings_from_kwargs(
                environment=given, secret_key=STRONG_TEST_SECRET
            )

    @pytest.mark.parametrize(
        "given", [0, 123, True, None, ["dev"], ("dev",), {"environment": "dev"}, b"dev"]
    )
    def test_non_string_profiles_rejected(self, given):
        with pytest.raises(ValidationError):
            build_settings_from_kwargs(
                environment=given, secret_key=STRONG_TEST_SECRET
            )

    def test_omitted_environment_keeps_local_dev_default(self):
        # CFG-01 permits the local dev default to remain. The production
        # assembly must still select its profile explicitly: every non-dev
        # build below passes ENVIRONMENT literally, and unknown values can
        # never fall through to either dev or production-like behavior.
        assert build_settings_from_kwargs().environment == "dev"


# ---------------------------------------------------------------------------
# Configuration: development origins (CFG-05).
# ---------------------------------------------------------------------------

class TestDevConfiguration:
    @pytest.mark.parametrize("profile", ["dev", "staging", "production"])
    @pytest.mark.parametrize("raw", ["null", "  null  "])
    def test_explicit_environment_null_is_rejected_at_source(self, profile, raw):
        with pytest.raises(ValueError, match="Explicit null CORS_ORIGINS"):
            build_settings_from_env({
                "ENVIRONMENT": profile, "SECRET_KEY": STRONG_TEST_SECRET,
                "CORS_ORIGINS": raw,
            })

    def test_dev_default_origins_exact_via_env(self):
        settings = build_settings_from_env(
            {"ENVIRONMENT": "dev", "SECRET_KEY": STRONG_TEST_SECRET}
        )
        assert settings.cors_origins == DEV_DEFAULT_ORIGINS

    def test_dev_default_origins_exact_via_kwarg(self):
        settings = build_settings_from_kwargs(
            environment="dev", secret_key=STRONG_TEST_SECRET
        )
        assert settings.cors_origins == DEV_DEFAULT_ORIGINS

    def test_dev_explicit_empty_list_accepted(self):
        settings = build_settings_from_kwargs(
            environment="dev", cors_origins=[], secret_key=STRONG_TEST_SECRET
        )
        assert settings.cors_origins == []

    def test_dev_explicit_null_is_rejected(self):
        with pytest.raises(ValidationError):
            build_settings_from_kwargs(
                environment="dev", cors_origins=None, secret_key=STRONG_TEST_SECRET
            )

    @pytest.mark.parametrize("input_value", [(), "https://a.synthetic.invalid", {"a": 1}, 7])
    def test_dev_non_list_input_rejected_before_coercion(self, input_value):
        with pytest.raises(ValidationError):
            build_settings_from_kwargs(
                environment="dev", cors_origins=input_value,
                secret_key=STRONG_TEST_SECRET,
            )

    @pytest.mark.parametrize(
        "origins",
        [
            ["https://clinic-app.synthetic.invalid"],
            ["https://clinic-app.synthetic.invalid:8443", "http://localhost:8080"],
            ["http://localhost", "http://127.0.0.1:3000", "http://[::1]:3000"],
            ["HTTPS://Mixed-Case.Synthetic.Invalid"],
            ["https://example.com:443"],
            ["http://[0:0:0:0:0:0:0:1]:080"],
            [
                "https://yurifrusin.github.io",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ],
        ],
    )
    def test_dev_valid_explicit_lists_are_canonical_for_middleware(self, origins):
        settings = build_settings_from_kwargs(
            environment="dev", cors_origins=list(origins),
            secret_key=STRONG_TEST_SECRET,
        )
        expected = [
            "https://mixed-case.synthetic.invalid" if origin == "HTTPS://Mixed-Case.Synthetic.Invalid"
            else "https://example.com" if origin == "https://example.com:443"
            else "http://[::1]" if origin == "http://[0:0:0:0:0:0:0:1]:080"
            else origin for origin in origins
        ]
        assert settings.cors_origins == expected

    @pytest.mark.parametrize(
        "origins",
        [
            ["*"],
            ["https://*.synthetic.invalid"],
            ["https://example.com/*"],
            ["not-an-origin"],
            ["https://"],
            ["https://?x"],
            ["://missing-scheme.invalid"],
            ["ftp://files.synthetic.invalid"],
            ["ws://sockets.synthetic.invalid"],
            ["https://user@host.synthetic.invalid"],
            ["https://user:pass@host.synthetic.invalid/"],
            ["https://host.synthetic.invalid/"],
            ["https://host.synthetic.invalid/app"],
            ["https://host.synthetic.invalid?a=b"],
            ["https://host.synthetic.invalid#frag"],
            ["https://clinic.synthetic.invalid?"],
            ["https://clinic.synthetic.invalid#"],
            ["\x01https://clinic.synthetic.invalid"],
            ["https://clinic.synthetic.invalid\x7f"],
            ["https://host.synthetic.invalid:99999"],
            ["https://host.synthetic.invalid:0"],
            ["https://host.synthetic.invalid:notaport"],
            ["https://host.synthetic.invalid:"],
            ["http://host.synthetic.invalid"],
            ["http://192.168.1.10"],
            ["http://[::1"],
            ["https://[::1]junk"],
            ["https://[::1]junk:443"],
            ["https://[v1.example]"],
            ["https://[127.0.0.1]"],
            [" https://host.synthetic.invalid"],
            ["https://host.synthetic.invalid "],
            ["https://ho st.synthetic.invalid"],
            [""],
            ["   "],
            ["https://dup.synthetic.invalid", "https://dup.synthetic.invalid"],
            ["HTTPS://DUP.synthetic.invalid", "https://dup.synthetic.invalid"],
            ["https://example.com", "https://example.com:443"],
            ["https://ok.synthetic.invalid", "https://ok.synthetic.invalid/"],
            [["https://nested.synthetic.invalid"]],
            [123],
            [None],
            [b"https://clinic.synthetic.invalid"],
            ["https://ok.synthetic.invalid", 123],
        ],
    )
    def test_dev_invalid_lists_rejected(self, origins):
        with pytest.raises(ValidationError):
            build_settings_from_kwargs(
                environment="dev", cors_origins=origins,
                secret_key=STRONG_TEST_SECRET,
            )

    def test_dev_json_list_env_contract_accepted(self):
        settings = build_settings_from_env(
            {
                "ENVIRONMENT": "dev",
                "SECRET_KEY": STRONG_TEST_SECRET,
                "CORS_ORIGINS": '["https://a.synthetic.invalid", "http://localhost:3000"]',
            }
        )
        assert settings.cors_origins == [
            "https://a.synthetic.invalid",
            "http://localhost:3000",
        ]

    def test_dev_json_empty_list_env_accepted(self):
        settings = build_settings_from_env(
            {
                "ENVIRONMENT": "dev",
                "SECRET_KEY": STRONG_TEST_SECRET,
                "CORS_ORIGINS": "[]",
            }
        )
        assert settings.cors_origins == []

    @pytest.mark.parametrize(
        "raw", ["{not-json", '"just-a-string"', "123", '{"a": 1}', "", "null"]
    )
    def test_dev_json_wrong_type_or_malformed_rejected(self, raw):
        with pytest.raises(ValueError):
            build_settings_from_env(
                {
                    "ENVIRONMENT": "dev",
                    "SECRET_KEY": STRONG_TEST_SECRET,
                    "CORS_ORIGINS": raw,
                }
            )


# ---------------------------------------------------------------------------
# Configuration: staging/production empty-only origins (CFG-02/03/04).
# ---------------------------------------------------------------------------

class TestNonDevConfiguration:
    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_omitted_resolves_to_empty_via_env(self, profile):
        settings = build_settings_from_env(
            {"ENVIRONMENT": profile, "SECRET_KEY": STRONG_TEST_SECRET}
        )
        assert settings.cors_origins == []

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_omitted_resolves_to_empty_via_kwarg(self, profile):
        settings = build_settings_from_kwargs(
            environment=profile, secret_key=STRONG_TEST_SECRET
        )
        assert settings.cors_origins == []

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_explicit_empty_list_accepted(self, profile):
        settings = build_settings_from_kwargs(
            environment=profile, cors_origins=[], secret_key=STRONG_TEST_SECRET
        )
        assert settings.cors_origins == []

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_explicit_null_rejected(self, profile):
        with pytest.raises(ValidationError):
            build_settings_from_kwargs(
                environment=profile, cors_origins=None, secret_key=STRONG_TEST_SECRET
            )

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_explicit_json_null_rejected(self, profile):
        with pytest.raises(ValueError):
            build_settings_from_env({
                "ENVIRONMENT": profile, "SECRET_KEY": STRONG_TEST_SECRET,
                "CORS_ORIGINS": "null",
            })

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    @pytest.mark.parametrize(
        "origins",
        [
            ["https://api.synthetic.invalid"],
            ["https://yurifrusin.github.io"],
            ["https://abc123.ngrok.io"],
            ["http://localhost:3000"],
            ["http://127.0.0.1:3000"],
            ["https://UPPER.synthetic.invalid"],
            ["*"],
            [" "],
            [""],
            ["https://a.synthetic.invalid", "not-an-origin"],
            ["https://a.synthetic.invalid", "https://a.synthetic.invalid"],
            [123],
            ["not-an-origin"],
        ],
    )
    def test_every_nonempty_list_rejected(self, profile, origins):
        with pytest.raises(ValidationError):
            build_settings_from_kwargs(
                environment=profile, cors_origins=origins,
                secret_key=STRONG_TEST_SECRET,
            )

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_nonempty_env_override_rejected(self, profile):
        with pytest.raises(ValidationError):
            build_settings_from_env(
                {
                    "ENVIRONMENT": profile,
                    "SECRET_KEY": STRONG_TEST_SECRET,
                    "CORS_ORIGINS": '["https://api.synthetic.invalid"]',
                }
            )


# ---------------------------------------------------------------------------
# Configuration: preserved secret and provider refusals (CFG-06).
# ---------------------------------------------------------------------------

class TestPreservedRefusals:
    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    @pytest.mark.parametrize(
        "secret_key", [OMITTED, "", PUBLIC_DEFAULT_SECRET],
        ids=["omitted-public-default", "empty", "explicit-public-default"],
    )
    def test_nondev_insecure_secret_refused(self, profile, secret_key):
        kwargs = {"environment": profile}
        if secret_key is not OMITTED:
            kwargs["secret_key"] = secret_key
        with pytest.raises(RuntimeError):
            build_settings_from_kwargs(**kwargs)

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_nondev_missing_or_empty_secret_refused_via_env(self, profile):
        with pytest.raises(RuntimeError):
            build_settings_from_env({"ENVIRONMENT": profile})
        with pytest.raises(RuntimeError):
            build_settings_from_env({"ENVIRONMENT": profile, "SECRET_KEY": ""})

    @pytest.mark.parametrize("profile", ALL_PROFILES)
    def test_strong_secret_control_accepted(self, profile):
        settings = build_settings_from_kwargs(
            environment=profile, secret_key=STRONG_TEST_SECRET
        )
        assert settings.environment == profile

    def test_dev_default_secret_control_accepted(self):
        settings = build_settings_from_kwargs(environment="dev")
        assert settings.secret_key == PUBLIC_DEFAULT_SECRET

    @pytest.mark.parametrize("profile", ALL_PROFILES)
    def test_provider_default_off_control_accepted(self, profile):
        settings = build_settings_from_kwargs(
            environment=profile, secret_key=STRONG_TEST_SECRET
        )
        assert settings.bernie_booking_interpreter_provider == "disabled"

    def test_unknown_provider_control_accepted(self):
        settings = build_settings_from_kwargs(
            environment="staging",
            secret_key=STRONG_TEST_SECRET,
            bernie_booking_interpreter_provider="definitely-not-a-provider",
        )
        assert (
            settings.bernie_booking_interpreter_provider
            == "definitely-not-a-provider"
        )

    @pytest.mark.parametrize("profile", ["dev", "production"])
    @pytest.mark.parametrize(
        "provider",
        ["gemini", "gemini_vertex", "vertex", "vertex_gemini", " GEMINI "],
    )
    def test_live_provider_refused(self, profile, provider):
        with pytest.raises(
            RuntimeError,
            match=r"^Bernie live-provider configuration is blocked by docs/bernie-interpretation-harness-runtime-gate\.json\.",
        ):
            build_settings_from_kwargs(
                environment=profile,
                secret_key=STRONG_TEST_SECRET,
                bernie_booking_interpreter_provider=provider,
            )


# ---------------------------------------------------------------------------
# Serving: non-dev negatives via actual ASGI requests (SRV-01, SRV-02).
# ---------------------------------------------------------------------------

class TestNonDevServingNegatives:
    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    @nondev_cors_input
    def test_taskpane_root_not_served(self, profile, cors_origins):
        built = build_profile_app(
            environment=profile, cors_origins=cors_origins
        )
        with _client_for(built) as client:
            for path in ("/taskpane", "/taskpane/"):
                _assert_not_served_without_redirect(client.get(path))

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    @nondev_cors_input
    def test_taskpane_child_asset_not_served(self, profile, cors_origins):
        built = build_profile_app(
            environment=profile, cors_origins=cors_origins
        )
        with _client_for(built) as client:
            _assert_not_served_without_redirect(client.get(TASKPANE_CHILD_URL))
            _assert_not_served_without_redirect(client.head(TASKPANE_CHILD_URL))

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    @nondev_cors_input
    def test_interactive_docs_not_served(self, profile, cors_origins):
        built = build_profile_app(
            environment=profile, cors_origins=cors_origins
        )
        with _client_for(built) as client:
            for path in INTERACTIVE_DOC_PATHS + ("/docs/",):
                _assert_not_served_without_redirect(client.get(path))

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    @nondev_cors_input
    @pytest.mark.parametrize("path", BERNIE_DEV_FIXTURE_PATHS)
    def test_dev_fixture_routes_not_served(self, profile, cors_origins, path):
        # The fixture router is neither imported nor included off-dev, so the
        # absence proof needs no credentials: 404 either way.
        built = build_profile_app(
            environment=profile, cors_origins=cors_origins
        )
        with _client_for(built) as client:
            _assert_not_served_without_redirect(client.get(path))


# ---------------------------------------------------------------------------
# Serving: retained health and machine schema (SRV-02, SRV-03).
# ---------------------------------------------------------------------------

class TestRetainedSurfaces:
    @pytest.mark.parametrize("profile", ALL_PROFILES)
    def test_health_retained(self, profile):
        built = build_profile_app(environment=profile)
        with _client_for(built) as client:
            response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "EMR4 Centaur API"}

    @pytest.mark.parametrize("profile", ALL_PROFILES)
    def test_openapi_retained_as_machine_schema(self, profile):
        built = build_profile_app(environment=profile)
        with _client_for(built) as client:
            response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        schema = response.json()
        assert "openapi" in schema
        assert isinstance(schema["paths"], dict)

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    @nondev_cors_input
    def test_openapi_excludes_dev_fixture_routes(self, profile, cors_origins):
        built = build_profile_app(
            environment=profile, cors_origins=cors_origins
        )
        with _client_for(built) as client:
            paths = client.get("/openapi.json").json()["paths"]
        for fixture_path in BERNIE_DEV_FIXTURE_PATHS:
            assert fixture_path not in paths

    def test_dev_openapi_includes_dev_fixture_routes(self):
        built = build_profile_app(environment="dev")
        with _client_for(built) as client:
            paths = client.get("/openapi.json").json()["paths"]
        for fixture_path in BERNIE_DEV_FIXTURE_PATHS:
            assert fixture_path in paths


# ---------------------------------------------------------------------------
# Serving: development positives (CFG-05).
# ---------------------------------------------------------------------------

class TestDevServingPositives:
    def test_taskpane_child_served_from_bound_path(self):
        bound_file = TASKPANE_DIR / TASKPANE_CHILD_NAME
        expected = bound_file.read_bytes()
        assert expected, f"bound taskpane fixture is missing: {bound_file}"
        built = build_profile_app(environment="dev")
        with _client_for(built) as client:
            response = client.get(TASKPANE_CHILD_URL)
        assert response.status_code == 200
        assert response.content == expected

    @pytest.mark.parametrize("path", INTERACTIVE_DOC_PATHS)
    def test_interactive_docs_served(self, path):
        built = build_profile_app(environment="dev")
        with _client_for(built) as client:
            response = client.get(path)
        assert response.status_code == 200

    @pytest.mark.parametrize("path", BERNIE_DEV_FIXTURE_PATHS)
    def test_dev_fixture_routes_registered(self, path):
        # Unauthenticated: the request must reach the auth gate (401), which
        # proves the router is included. 401 here is the positive signal;
        # 404 would mean the route is absent.
        built = build_profile_app(environment="dev")
        with _client_for(built) as client:
            response = client.get(path)
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Serving: authenticated-API boundary (SRV-03/AUTH-01/AUTH-02/SRV-04 partial).
# ---------------------------------------------------------------------------

class TestAuthenticatedApiBoundary:
    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_real_password_jwt_and_current_user_on_disposable_postgres(
        self, profile, production_profile_runtime
    ):
        """Required real-auth positive; missing reviewed fixture is an error.

        The external runner owns database creation/migration, synthetic user
        seeding, exact executable and network binding, and final disposal.
        This test never overrides get_current_user or get_db.
        """
        runtime = production_profile_runtime
        required = {
            "database_url", "database_name", "application_role", "user_email",
            "password", "expected_user_id", "expected_practice_id", "expected_role",
        }
        assert isinstance(runtime, Mapping) and set(runtime) == required
        url = make_url(runtime["database_url"])
        assert url.get_backend_name() == "postgresql"
        assert url.host in {"127.0.0.1", "::1"}
        assert isinstance(url.port, int) and 1 <= url.port <= 65535
        assert url.database == runtime["database_name"]
        assert url.database.startswith("g2_profile_")
        assert url.username == runtime["application_role"]
        assert runtime["user_email"].endswith(".invalid")
        assert runtime["password"] and runtime["password"] != PUBLIC_DEFAULT_SECRET
        expected_user = str(uuid.UUID(runtime["expected_user_id"]))
        expected_practice = str(uuid.UUID(runtime["expected_practice_id"]))
        built = build_profile_app(environment=profile, database_url=runtime["database_url"])
        with _client_for(built) as client:
            with built.database_engine.connect() as connection:
                identity = connection.execute(sql_text("SELECT current_database(), current_user")).one()
            assert tuple(identity) == (runtime["database_name"], runtime["application_role"])
            login = client.post(
                "/api/v1/auth/login",
                data={"username": runtime["user_email"], "password": runtime["password"]},
            )
            assert login.status_code == 200
            token = login.json()["access_token"]
            assert isinstance(token, str) and token
            me = client.get(MEANINGFUL_ME_URL, headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json() == {
            "id": expected_user, "email": runtime["user_email"],
            "role": runtime["expected_role"], "practice_id": expected_practice,
        }

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_me_succeeds_through_isolated_stubbed_identity(self, profile):
        # Representative retained-API positive. The stubbed identity proves
        # route retention and auth-dependency wiring only; real password/JWT
        # verification stays pending on the Step 3 database binding.
        built = build_profile_app(environment=profile)
        with _client_for(built) as client:
            with isolated_stubbed_identity(built):
                response = client.get(
                    MEANINGFUL_ME_URL,
                    headers={"Authorization": "Bearer stubbed-isolated-synthetic"},
                )
        assert response.status_code == 200
        assert response.json() == {
            "id": str(STUB_USER_ID),
            "email": STUB_EMAIL,
            "role": STUB_ROLE,
            "practice_id": str(STUB_PRACTICE_ID),
        }

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_me_rejects_missing_credentials(self, profile):
        built = build_profile_app(environment=profile)
        with _client_for(built) as client:
            response = client.get(MEANINGFUL_ME_URL)
        assert response.status_code == 401

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    def test_me_rejects_invalid_token_before_database_access(self, profile):
        # The real auth dependency runs; the fail-on-access Engine.connect
        # boundary counts and rejects any attempted database operation.
        built = build_profile_app(environment=profile)
        with _client_for(built) as client:
            response = client.get(
                MEANINGFUL_ME_URL,
                headers={"Authorization": "Bearer invalid-synthetic-token"},
            )
        _assert_invalid_auth_has_no_db_access(response, built)

    def test_invalid_auth_oracle_rejects_database_before_401_counterexample(self):
        built = build_profile_app(environment="production")
        with _client_for(built) as client:
            def bad_auth(db=Depends(built.get_db)):
                try:
                    db.execute(sql_text("SELECT 1"))
                except AssertionError:
                    pass
                raise HTTPException(status_code=401, detail="authored bad ordering")

            built.app.dependency_overrides[built.get_current_user] = bad_auth
            response = client.get(MEANINGFUL_ME_URL)
            assert response.status_code == 401
            with pytest.raises(AssertionError, match="attempted database access"):
                _assert_invalid_auth_has_no_db_access(response, built)
            assert built.db_accesses == 1

    def test_rejection_is_independent_of_origin(self):
        # SRV-04: invalid authentication is rejected irrespective of Origin,
        # and the rejection carries no cross-origin permission.
        built = build_profile_app(environment="production")
        with _client_for(built) as client:
            response = client.get(
                MEANINGFUL_ME_URL,
                headers={"Origin": "https://synthetic-consumer.invalid"},
            )
        assert response.status_code == 401
        assert "access-control-allow-origin" not in response.headers

    def test_authorized_call_succeeds_regardless_of_cors(self):
        # SRV-04: CORS grants no cross-origin permission off-dev, and that
        # CORS outcome does not authenticate or block the authorized call.
        built = build_profile_app(environment="production")
        with _client_for(built) as client:
            with isolated_stubbed_identity(built):
                response = client.get(
                    MEANINGFUL_ME_URL,
                    headers={
                        "Authorization": "Bearer stubbed-isolated-synthetic",
                        "Origin": "https://synthetic-consumer.invalid",
                    },
                )
        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers


# ---------------------------------------------------------------------------
# Serving: CORS policy (SRV-04, CFG-05).
# ---------------------------------------------------------------------------

class TestCorsPolicy:
    def test_custom_mixed_case_origin_matches_canonical_browser_origin(self):
        built = build_profile_app(
            environment="dev",
            cors_origins=["HTTPS://Mixed-Case.Synthetic.Invalid:443"],
        )
        with _client_for(built) as client:
            assert built.settings.cors_origins == ["https://mixed-case.synthetic.invalid"]
            allowed = client.options(
                MEANINGFUL_ME_URL,
                headers={"Origin": "https://mixed-case.synthetic.invalid",
                         "Access-Control-Request-Method": "GET"},
            )
            denied = client.options(
                MEANINGFUL_ME_URL,
                headers={"Origin": "https://other.synthetic.invalid",
                         "Access-Control-Request-Method": "GET"},
            )
        assert allowed.status_code == 200
        assert allowed.headers.get("access-control-allow-origin") == "https://mixed-case.synthetic.invalid"
        assert allowed.headers.get("access-control-allow-credentials") == "true"
        assert "access-control-allow-origin" not in denied.headers

    @pytest.mark.parametrize("origin", DEV_DEFAULT_ORIGINS)
    def test_dev_origin_receives_exact_credentialed_response(self, origin):
        built = build_profile_app(environment="dev")
        with _client_for(built) as client:
            response = client.options(
                MEANINGFUL_ME_URL,
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                },
            )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == origin
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_dev_explicit_empty_list_serves_no_allow_origin(self):
        built = build_profile_app(environment="dev", cors_origins=[])
        with _client_for(built) as client:
            response = client.options(
                MEANINGFUL_ME_URL,
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )
        assert "access-control-allow-origin" not in response.headers

    @pytest.mark.parametrize("profile", NONDEV_PROFILES)
    @nondev_cors_input
    @pytest.mark.parametrize(
        "origin",
        ["http://localhost:3000", "https://synthetic-consumer.invalid"],
        ids=["former-dev-default", "valid-https"],
    )
    def test_nondev_emits_no_allow_origin(self, profile, cors_origins, origin):
        built = build_profile_app(
            environment=profile, cors_origins=cors_origins
        )
        with _client_for(built) as client:
            response = client.options(
                MEANINGFUL_ME_URL,
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                },
            )
        assert "access-control-allow-origin" not in response.headers
