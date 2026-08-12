"""Pure ASGI after-send seam for the globally-disabled shadow scaffold."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from app.services.diary.shadow_instrumentation import (
    ShadowInstrumentationRuntime,
    shadow_instrumentation_runtime,
)


AsgiMessage = MutableMapping[str, Any]
AsgiReceive = Callable[[], Awaitable[AsgiMessage]]
AsgiSend = Callable[[AsgiMessage], Awaitable[None]]
AsgiApp = Callable[[AsgiMessage, AsgiReceive, AsgiSend], Awaitable[None]]


class ShadowAfterSendMiddleware:
    """Delegate unchanged while disabled; otherwise offer only after final send."""

    def __init__(
        self,
        app: AsgiApp,
        runtime: ShadowInstrumentationRuntime = shadow_instrumentation_runtime,
    ) -> None:
        self.app = app
        self.runtime = runtime

    async def __call__(
        self,
        scope: AsgiMessage,
        receive: AsgiReceive,
        send: AsgiSend,
    ) -> None:
        if scope.get("type") != "http" or not self.runtime.is_globally_enabled():
            await self.app(scope, receive, send)
            return

        token, cell = self.runtime.bind_request_cell()
        final_body_seen = False

        async def send_then_offer(message: AsgiMessage) -> None:
            nonlocal final_body_seen
            await send(message)
            if (
                not final_body_seen
                and message.get("type") == "http.response.body"
                and not message.get("more_body", False)
            ):
                final_body_seen = True
                try:
                    self.runtime.offer_staged_after_send(cell)
                except Exception:
                    return

        try:
            await self.app(scope, receive, send_then_offer)
        finally:
            self.runtime.reset_request_cell(token)
