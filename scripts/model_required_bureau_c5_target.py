"""Bureau C5 fixed disposable loopback target module (frozen service artifact).

This module is the single C5-authored service artifact. It serves exactly one
health path and one closed JSON shape, and it is never executed in the
implementation-readiness tranche: it is structurally source-inspected and its
LF-byte SHA-256 is bound as the frozen service-artifact digest before any live
execution can be considered.

The module imports only the Python standard library. It imports no ``app``
package, product settings, database, provider or cloud module and accepts no
caller payload. It validates the exact constant host, the OS-assigned
server-held port, the opaque target nonce and the exact generation argument.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ENVIRONMENT = "c5_disposable_authored_synthetic"
TARGET_KIND = "task_owned_loopback_http_service"
TARGET_ID = "synthetic:c5-recovery-target"
HOST = "127.0.0.1"
HEALTH_PATH = "/healthz"
STATE_HEALTHY = "healthy"
HEALTH_SCHEMA_VERSION = "emr4.c5_health_body.v1"
ALLOWED_GENERATIONS = (1, 2)
_NONCE_RE = re.compile(r"^[0-9a-f]{32,64}$")


def compute_artifact_sha256() -> str:
    """Return the LF-byte SHA-256 of this frozen module.

    The digest is computed from the module's own file bytes at runtime so the
    closed health body always reports the exact frozen artifact digest without
    a hard-coded self-referential constant.  The module is never executed in
    this implementation tranche.
    """
    return hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()


class _HealthHandler(BaseHTTPRequestHandler):
    """One fixed health read carrying no input data and one closed JSON body."""

    server_version = "C5Health/1.0"

    def do_GET(self) -> None:
        if self.path != HEALTH_PATH:
            self.send_response(404)
            self.end_headers()
            return
        payload = {
            "schema_version": HEALTH_SCHEMA_VERSION,
            "environment": ENVIRONMENT,
            "kind": TARGET_KIND,
            "target_id": TARGET_ID,
            "host": HOST,
            "port": self.server.server_address[1],
            "nonce": self.server.nonce,
            "generation": self.server.generation,
            "artifact_sha256": compute_artifact_sha256(),
            "state": STATE_HEALTHY,
        }
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        # The closed health body is the only output; suppress default stderr logs.
        return None


class C5LoopbackServer(HTTPServer):
    """Loopback-only HTTPServer carrying the server-held nonce and generation."""

    def __init__(self, server_address, handler_class, *, nonce: str, generation: int):
        self.nonce = nonce
        self.generation = generation
        super().__init__(server_address, handler_class)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="C5 disposable loopback target (never run in the readiness tranche)"
    )
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--nonce", required=True)
    parser.add_argument("--generation", type=int, required=True)
    args = parser.parse_args(argv)

    if args.host != HOST:
        raise SystemExit("host must be exactly 127.0.0.1")
    if not _NONCE_RE.match(args.nonce):
        raise SystemExit("nonce must be an opaque hexadecimal value")
    if args.generation not in ALLOWED_GENERATIONS:
        raise SystemExit("generation must be exactly 1 or 2")
    if not isinstance(args.port, int) or args.port <= 0 or args.port > 65535:
        raise SystemExit("port must be an OS-assigned server-held ephemeral port")

    with C5LoopbackServer(
        (args.host, args.port),
        _HealthHandler,
        nonce=args.nonce,
        generation=args.generation,
    ) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
