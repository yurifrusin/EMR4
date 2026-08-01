"""Credential-free exact-path relay from the isolated cell to the host broker."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import http.client
import os
from pathlib import Path
import time


LISTEN_PORT = 8080
FORWARD_HOST = "host.docker.internal"
FORWARD_PORT = int(os.environ["BROKER_HOST_PORT"])
TOKEN_PATH = Path("/run/secrets/broker_token")
MAX_BYTES = 32768
HOST_CONNECT_ATTEMPTS = 100
HOST_CONNECT_DELAY_SECONDS = 0.1


def _post_to_host(
    body: bytes,
    token: str,
) -> tuple[http.client.HTTPConnection, http.client.HTTPResponse]:
    """Retry only a refusal that occurs before the request can be sent."""

    for attempt in range(HOST_CONNECT_ATTEMPTS):
        connection = http.client.HTTPConnection(
            FORWARD_HOST, FORWARD_PORT, timeout=30
        )
        try:
            connection.request(
                "POST",
                "/v1/execute",
                body=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body)),
                },
            )
        except ConnectionRefusedError:
            connection.close()
            if attempt + 1 == HOST_CONNECT_ATTEMPTS:
                raise
            time.sleep(HOST_CONNECT_DELAY_SECONDS)
            continue
        return connection, connection.getresponse()
    raise RuntimeError("host_connect_attempts_exhausted")


class RelayHandler(BaseHTTPRequestHandler):
    server_version = "AriadneRelay/1"

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/execute":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if size < 1 or size > MAX_BYTES:
            self.send_error(413)
            return
        body = self.rfile.read(size)
        token = TOKEN_PATH.read_text(encoding="utf-8").strip()
        connection, response = _post_to_host(body, token)
        response_body = response.read(32768)
        self.send_response(response.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)
        connection.close()
        self.server.shutdown_requested = True  # type: ignore[attr-defined]


def main() -> None:
    # nosec B104 -- container-only listener; no port is published and the
    # relay is attached only to the exact internal work-cell network.
    server = ThreadingHTTPServer(("0.0.0.0", LISTEN_PORT), RelayHandler)  # nosec B104
    server.shutdown_requested = False  # type: ignore[attr-defined]
    while not server.shutdown_requested:  # type: ignore[attr-defined]
        server.handle_request()
    server.server_close()


if __name__ == "__main__":
    main()
