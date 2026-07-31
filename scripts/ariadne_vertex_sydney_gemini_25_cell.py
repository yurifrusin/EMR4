"""Run one credential-free typed exchange with the one-use relay."""

from __future__ import annotations

import http.client
import json
from pathlib import Path
import time


ROOT = Path("/workspace")
REQUEST_PATH = ROOT / "cell-request.json"
MAX_RESPONSE_BYTES = 32768
RELAY_CONNECT_ATTEMPTS = 100
RELAY_CONNECT_DELAY_SECONDS = 0.1


def _post_to_relay(body: bytes) -> http.client.HTTPResponse:
    """Connect through the relay, retrying only a pre-connect refusal."""

    for attempt in range(RELAY_CONNECT_ATTEMPTS):
        connection = http.client.HTTPConnection("broker", 8080, timeout=25)
        try:
            connection.request(
                "POST",
                "/v1/execute",
                body=body,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body)),
                },
            )
        except ConnectionRefusedError:
            connection.close()
            if attempt + 1 == RELAY_CONNECT_ATTEMPTS:
                raise
            time.sleep(RELAY_CONNECT_DELAY_SECONDS)
            continue
        return connection.getresponse()
    raise RuntimeError("relay_connect_attempts_exhausted")


def main() -> int:
    body = REQUEST_PATH.read_bytes()
    response = _post_to_relay(body)
    raw = response.read(MAX_RESPONSE_BYTES)
    response.close()
    try:
        packet = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"status": "edge_aborted", "reason": "invalid_json"}))
        return 2
    if response.status != 200 or packet.get("status") != "completed":
        print(
            json.dumps(
                {
                    "status": "edge_aborted",
                    "reason": packet.get("reason_code", "broker_rejected"),
                    "broker_status": response.status,
                },
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(packet, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
