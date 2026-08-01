"""Supervised Office-host harness for the authored-synthetic cookie lifecycle.

This module is intentionally separate from the product application. It exposes
only the accepted application-auth router, two taskpane pages and a closed
evidence endpoint backed by process-local authored-synthetic state.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import secrets
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.routers.application_auth import (
    get_application_auth_operational_hardening,
    get_application_auth_transport,
    router as application_auth_router,
)
from app.services.application_auth_operational_hardening import (
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    ProxyTrustPolicy,
    TransportDenialEvent,
)
from app.services.application_auth_runtime import (
    AUTHORED_SYNTHETIC_DATA_CLASS,
    InMemoryAuthAuditSink,
    InMemoryAuthoredSyntheticStore,
    Surface,
    SyntheticPrincipal,
)
from app.services.application_auth_role_runtime import ApplicationAuthTransportRuntime
from app.services.application_auth_transport import (
    ApplicationAuthTransport,
    OneUseSyntheticBootstrapRegistry,
    TransportRequestDenied,
)


ASSET_ROOT = REPO_ROOT / "EMR4 Sidebar" / "assets"
TASKPANE_SCRIPT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "shared-application-auth-office-cookie-compatibility"
    / "taskpane.js"
)
DEVELOPMENT_ORIGIN = "https://property-cinch-backfield.ngrok-free.dev"
SURFACES = (Surface.WORD_DESKTOP, Surface.WORD_ONLINE)
_NO_STORE_HEADERS = {
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}
_TASKPANE_CSP = (
    "default-src 'none'; "
    "script-src 'self' https://appsforoffice.microsoft.com; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'"
)


class CompatibilityResultSubmission(BaseModel):
    """Closed browser-to-harness result; the nonce is never retained."""

    model_config = ConfigDict(extra="forbid")

    evidence_nonce: str
    surface: Literal[Surface.WORD_DESKTOP, Surface.WORD_ONLINE]
    host_class: Literal["installed_word", "word_online"]
    terminal_status: Literal["passed", "failed"]
    csrf_issued: bool
    session_created: bool
    first_validation_passed: bool
    rotation_passed: bool
    second_validation_passed: bool
    logout_passed: bool
    post_logout_denied: bool
    result_submitted: bool = True
    failure_code: Literal[
        "none",
        "office_unavailable",
        "office_host_mismatch",
        "bootstrap_unavailable",
        "csrf_failed",
        "login_failed",
        "first_validation_failed",
        "rotation_failed",
        "second_validation_failed",
        "logout_failed",
        "post_logout_validation_succeeded",
        "network_unavailable",
        "unexpected_response",
    ]


class SanitizedCompatibilityResult(BaseModel):
    """Durable-safe result with no raw nonce, URL, cookie or Office identity."""

    model_config = ConfigDict(extra="forbid")

    surface: Literal[Surface.WORD_DESKTOP, Surface.WORD_ONLINE]
    host_class: Literal["installed_word", "word_online"]
    terminal_status: Literal["passed", "failed"]
    csrf_issued: bool
    session_created: bool
    first_validation_passed: bool
    rotation_passed: bool
    second_validation_passed: bool
    logout_passed: bool
    post_logout_denied: bool
    result_submitted: bool
    failure_code: str


@dataclass
class _LaunchMaterial:
    bootstrap_value: str | None
    evidence_nonce: str | None
    evidence_nonce_hash: str
    page_delivered: bool = False


class _InMemoryDenialSink:
    def __init__(self) -> None:
        self._events: list[TransportDenialEvent] = []
        self._lock = threading.Lock()

    def record(self, event: TransportDenialEvent) -> None:
        with self._lock:
            self._events.append(event)

    def count(self) -> int:
        with self._lock:
            return len(self._events)


class _SurfaceBoundApplicationAuthTransport(ApplicationAuthTransport):
    """Bind each task bootstrap hash to its one frozen Office surface."""

    def __init__(
        self,
        *,
        bootstrap_surfaces: dict[str, Surface],
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._bootstrap_surfaces = {
            self._bootstrap_hash(value): surface
            for value, surface in bootstrap_surfaces.items()
        }

    @staticmethod
    def _bootstrap_hash(value: str) -> str:
        return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"

    def login(
        self,
        *,
        bootstrap_credential: str,
        surface: Surface,
        origin: str,
        correlation_id: str | None,
    ):
        expected = self._bootstrap_surfaces.get(
            self._bootstrap_hash(bootstrap_credential)
        )
        if expected is not surface:
            raise TransportRequestDenied()
        return super().login(
            bootstrap_credential=bootstrap_credential,
            surface=surface,
            origin=origin,
            correlation_id=correlation_id,
        )


class OfficeCookieCompatibilityHarnessBase:
    """Own the runtime-independent Office taskpane and result lifecycle."""

    def __init__(
        self,
        *,
        origin: str = DEVELOPMENT_ORIGIN,
        principal_namespace: Literal["office", "office-postgres"],
        launch_value_sink: Callable[[str], None] | None = None,
    ) -> None:
        if origin != DEVELOPMENT_ORIGIN:
            raise ValueError("the Office compatibility origin is frozen")
        self.origin = origin
        self._lock = threading.Lock()
        self._results: dict[Surface, SanitizedCompatibilityResult] = {}

        credentials: dict[str, SyntheticPrincipal] = {}
        bootstrap_surfaces: dict[str, Surface] = {}
        self._launches: dict[Surface, _LaunchMaterial] = {}
        for surface in SURFACES:
            bootstrap = secrets.token_urlsafe(32)
            nonce = secrets.token_urlsafe(32)
            if launch_value_sink is not None:
                launch_value_sink(bootstrap)
                launch_value_sink(nonce)
            surface_label = surface.value.replace("_", "-")
            credentials[bootstrap] = SyntheticPrincipal(
                user_id=f"synthetic-user-{principal_namespace}-{surface_label}",
                practice_id=f"synthetic-practice-{principal_namespace}-{surface_label}",
                current_backend_role="GP",
                practitioner_id=(
                    f"synthetic-practitioner-{principal_namespace}-{surface_label}"
                ),
            )
            bootstrap_surfaces[bootstrap] = surface
            self._launches[surface] = _LaunchMaterial(
                bootstrap_value=bootstrap,
                evidence_nonce=nonce,
                evidence_nonce_hash=self._hash(nonce),
            )

        self._initial_credentials = credentials
        self._initial_bootstrap_surfaces = bootstrap_surfaces
        self._surface_origins = {surface: origin for surface in Surface}

    def _take_initial_auth_material(
        self,
    ) -> tuple[
        dict[str, SyntheticPrincipal],
        dict[str, Surface],
        dict[Surface, str],
    ]:
        credentials = self._initial_credentials
        bootstrap_surfaces = self._initial_bootstrap_surfaces
        origins = self._surface_origins
        del self._initial_credentials
        del self._initial_bootstrap_surfaces
        del self._surface_origins
        return credentials, bootstrap_surfaces, origins

    @staticmethod
    def _hash(value: str) -> str:
        return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"

    @staticmethod
    def _expected_host_class(surface: Surface) -> str:
        return "installed_word" if surface is Surface.WORD_DESKTOP else "word_online"

    def deliver_taskpane(self, surface: Surface) -> str:
        with self._lock:
            material = self._launches[surface]
            if material.page_delivered:
                bootstrap = ""
                nonce = ""
            else:
                bootstrap = material.bootstrap_value or ""
                nonce = material.evidence_nonce or ""
                material.bootstrap_value = None
                material.evidence_nonce = None
                material.page_delivered = True
        return self._taskpane_html(surface, bootstrap, nonce)

    def record_result(
        self,
        submission: CompatibilityResultSubmission,
    ) -> SanitizedCompatibilityResult:
        surface = Surface(submission.surface)
        if submission.host_class != self._expected_host_class(surface):
            raise HTTPException(status_code=400, detail="result_not_admitted")
        supplied_hash = self._hash(submission.evidence_nonce)
        with self._lock:
            material = self._launches[surface]
            if not secrets.compare_digest(
                supplied_hash,
                material.evidence_nonce_hash,
            ):
                raise HTTPException(status_code=400, detail="result_not_admitted")
            if surface in self._results:
                raise HTTPException(status_code=409, detail="result_already_recorded")
            result = SanitizedCompatibilityResult(
                **submission.model_dump(exclude={"evidence_nonce"})
            )
            passed_steps = all(
                (
                    result.csrf_issued,
                    result.session_created,
                    result.first_validation_passed,
                    result.rotation_passed,
                    result.second_validation_passed,
                    result.logout_passed,
                    result.post_logout_denied,
                    result.result_submitted,
                )
            )
            if (result.terminal_status == "passed") != passed_steps:
                raise HTTPException(status_code=400, detail="result_not_admitted")
            if (result.failure_code == "none") != passed_steps:
                raise HTTPException(status_code=400, detail="result_not_admitted")
            self._results[surface] = result
            return result

    def evidence(self) -> dict[str, object]:
        raise NotImplementedError

    def _taskpane_html(
        self,
        surface: Surface,
        bootstrap: str,
        evidence_nonce: str,
    ) -> str:
        expected_host = self._expected_host_class(surface)
        return f"""<!doctype html>
<html lang="en-AU">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Raisa Office cookie compatibility</title>
  <script src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"></script>
  <link rel="stylesheet" href="/office-cookie-compatibility/taskpane.css">
</head>
<body>
  <main id="compatibility-root"
        data-surface="{html.escape(surface.value, quote=True)}"
        data-expected-host="{html.escape(expected_host, quote=True)}"
        data-bootstrap="{html.escape(bootstrap, quote=True)}"
        data-evidence-nonce="{html.escape(evidence_nonce, quote=True)}">
    <p class="eyebrow">Development-only security check</p>
    <h1><span>Raisa</span><i aria-hidden="true"></i> medical office</h1>
    <p class="lede">Verify the authored-synthetic session-cookie lifecycle in this Office host.</p>
    <dl>
      <div><dt>Expected surface</dt><dd id="surface-label">{html.escape(surface.value)}</dd></div>
      <div><dt>Office host</dt><dd id="host-label">Waiting for Office</dd></div>
      <div><dt>Session state</dt><dd id="state-label">Not started</dd></div>
    </dl>
    <button id="run-check" type="button" disabled>Run compatibility check</button>
    <p id="status" role="status" aria-live="polite">Confirming the Office host…</p>
    <p class="boundary">No document, patient, product, provider or real identity data is used.</p>
  </main>
  <script src="/office-cookie-compatibility/taskpane.js"></script>
</body>
</html>"""


class OfficeCookieCompatibilityHarness(OfficeCookieCompatibilityHarnessBase):
    """Own one process-local in-memory Office compatibility generation."""

    def __init__(self, *, origin: str = DEVELOPMENT_ORIGIN) -> None:
        super().__init__(origin=origin, principal_namespace="office")
        credentials, bootstrap_surfaces, origins = self._take_initial_auth_material()
        self.store = InMemoryAuthoredSyntheticStore(
            data_class=AUTHORED_SYNTHETIC_DATA_CLASS
        )
        self.auth_audit = InMemoryAuthAuditSink(
            data_class=AUTHORED_SYNTHETIC_DATA_CLASS
        )
        runtime = ApplicationAuthTransportRuntime(
            store=self.store,
            audit_sink=self.auth_audit,
            surface_origins=origins,
        )
        self.bootstrap_registry = OneUseSyntheticBootstrapRegistry(credentials)
        self.transport = _SurfaceBoundApplicationAuthTransport(
            runtime=runtime,  # type: ignore[arg-type]
            bootstrap_registry=self.bootstrap_registry,
            surface_origins=origins,
            bootstrap_surfaces=bootstrap_surfaces,
        )
        self.denial_audit = _InMemoryDenialSink()
        self.guard = ApplicationAuthOperationalHardening(
            proxy_policy=ProxyTrustPolicy.from_cidrs(
                ["127.0.0.0/8", "::1/128"]
            ),
            rate_limiter=BoundedFixedWindowRateLimiter(
                requests_per_window=64,
                window_seconds=300,
                max_keys=64,
            ),
            denial_audit_sink=self.denial_audit,
            client_hmac_key=secrets.token_bytes(32),
        )

    def evidence(self) -> dict[str, object]:
        with self._lock:
            results = {
                surface.value: (
                    self._results[surface].model_dump(mode="json")
                    if surface in self._results
                    else {"terminal_status": "pending"}
                )
                for surface in SURFACES
            }
        registry = self.bootstrap_registry.state_counts()
        return {
            "schema_version": "emr4.office_cookie_compatibility_evidence.v1",
            "data_class": AUTHORED_SYNTHETIC_DATA_CLASS,
            "runtime_class": "provider_free_process_local_in_memory",
            "development_origin": self.origin,
            "results": results,
            "bootstrap_registry_counts": registry,
            "auth_audit_event_count": len(self.auth_audit.snapshot()),
            "denial_audit_event_count": self.denial_audit.count(),
            "side_effects": {
                "provider_calls": 0,
                "external_identity_calls": 0,
                "product_or_database_reads": 0,
                "document_reads": 0,
                "document_writes": 0,
                "product_commands": 0,
                "cloud_or_iam_mutations": 0,
                "deployments": 0,
                "production_changes": 0,
            },
        }

def build_app(
    harness: OfficeCookieCompatibilityHarnessBase | None = None,
) -> FastAPI:
    selected = harness or OfficeCookieCompatibilityHarness()
    app = FastAPI(
        title="Raisa authored-synthetic Office cookie compatibility",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.office_cookie_compatibility = selected
    app.include_router(application_auth_router)
    app.dependency_overrides[get_application_auth_transport] = lambda: selected.transport
    app.dependency_overrides[
        get_application_auth_operational_hardening
    ] = lambda: selected.guard

    @app.get("/office-cookie-compatibility/taskpane", response_class=HTMLResponse)
    def taskpane(
        surface: Surface = Query(...),
    ) -> HTMLResponse:
        if surface not in SURFACES:
            raise HTTPException(status_code=404, detail="surface_not_available")
        return HTMLResponse(
            selected.deliver_taskpane(surface),
            headers={**_NO_STORE_HEADERS, "Content-Security-Policy": _TASKPANE_CSP},
        )

    @app.get("/office-cookie-compatibility/taskpane.js")
    def taskpane_script() -> FileResponse:
        return FileResponse(
            TASKPANE_SCRIPT,
            media_type="text/javascript",
            headers=_NO_STORE_HEADERS,
        )

    @app.get("/office-cookie-compatibility/taskpane.css")
    def taskpane_css() -> Response:
        return Response(
            _TASKPANE_CSS,
            media_type="text/css",
            headers=_NO_STORE_HEADERS,
        )

    @app.get("/office-cookie-compatibility/icon/{size}.png")
    def icon(size: Literal[16, 32, 64, 80]) -> FileResponse:
        return FileResponse(
            ASSET_ROOT / f"icon-{size}.png",
            media_type="image/png",
            headers=_NO_STORE_HEADERS,
        )

    @app.post(
        "/office-cookie-compatibility/result",
        response_model=SanitizedCompatibilityResult,
        status_code=status.HTTP_201_CREATED,
    )
    def record_result(
        submission: CompatibilityResultSubmission,
        origin: str | None = Header(default=None, alias="Origin"),
    ) -> SanitizedCompatibilityResult:
        if origin != selected.origin:
            raise HTTPException(status_code=403, detail="result_not_admitted")
        return selected.record_result(submission)

    @app.get("/office-cookie-compatibility/evidence")
    def evidence(request: Request) -> JSONResponse:
        forwarded = any(
            name in request.headers
            for name in ("x-forwarded-for", "x-forwarded-host", "x-forwarded-proto")
        )
        if (
            request.client is None
            or request.client.host not in {"127.0.0.1", "::1", "testclient"}
            or request.url.hostname not in {"127.0.0.1", "::1", "localhost"}
            or forwarded
        ):
            raise HTTPException(status_code=404, detail="evidence_not_available")
        return JSONResponse(selected.evidence(), headers=_NO_STORE_HEADERS)

    return app


_TASKPANE_CSS = """
:root { color-scheme: light; font-family: "Source Sans 3", "Segoe UI", sans-serif; }
* { box-sizing: border-box; }
body { margin: 0; background: #f6f7f9; color: #171b2d; }
main { min-height: 100vh; padding: 28px 22px; border-top: 6px solid #f1c10c; }
.eyebrow { margin: 0 0 18px; color: #596174; font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
h1 { margin: 0; font-size: 28px; font-weight: 400; line-height: 1.05; }
h1 span { font-weight: 700; }
h1 i { display: inline-block; width: 8px; height: 8px; margin: 0 5px 3px; border-radius: 50%; background: #f1c10c; }
.lede { max-width: 34ch; margin: 12px 0 24px; color: #4f5768; line-height: 1.45; }
dl { margin: 0 0 24px; border: 1px solid #d8dce5; border-radius: 10px; background: #fff; overflow: hidden; }
dl div { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 11px 13px; border-bottom: 1px solid #e7e9ef; }
dl div:last-child { border: 0; }
dt { color: #646c7d; }
dd { margin: 0; text-align: right; font-weight: 650; overflow-wrap: anywhere; }
button { width: 100%; min-height: 44px; border: 0; border-radius: 8px; background: #171b2d; color: #fff; font: inherit; font-weight: 700; cursor: pointer; }
button:hover:not(:disabled) { background: #292f48; }
button:focus-visible { outline: 3px solid #f1c10c; outline-offset: 3px; }
button:disabled { cursor: not-allowed; opacity: .45; }
#status { min-height: 42px; margin: 14px 0 0; line-height: 1.4; }
.boundary { margin: 24px 0 0; padding-top: 16px; border-top: 1px solid #d8dce5; color: #697184; font-size: 12px; line-height: 1.4; }
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the task-owned Office cookie-compatibility harness."
    )
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be in 1024..65535")
    uvicorn.run(
        build_app(),
        host="127.0.0.1",
        port=args.port,
        proxy_headers=False,
        access_log=False,
        log_level="warning",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CompatibilityResultSubmission",
    "DEVELOPMENT_ORIGIN",
    "OfficeCookieCompatibilityHarness",
    "OfficeCookieCompatibilityHarnessBase",
    "SanitizedCompatibilityResult",
    "build_app",
]
