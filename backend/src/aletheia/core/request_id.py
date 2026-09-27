import uuid

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware:
    """Assigns a server-generated identifier to every HTTP request.

    The identifier is stored in the request state and returned in the
    X-Request-ID response header so clients can report it and it can be
    correlated with server logs. Client-supplied values are ignored.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message).setdefault(REQUEST_ID_HEADER, request_id)
            await send(message)

        await self.app(scope, receive, send_with_request_id)


def get_request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unknown"))
