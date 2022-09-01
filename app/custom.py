import json
from typing import Optional, Mapping, Callable, Any

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask
from starlette.types import Receive, Scope, Send
from dicttoxml import dicttoxml
import xmltodict

class CustomResponse(Response):
    media_type = "application/xml"

    def __init__(self, content: Any = None, status_code: int = 200, headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None, background: Optional[BackgroundTask] = None, custom_root: Optional[str] = 'user') -> None:
        self.custom_root = custom_root
        super().__init__(content, status_code, headers, media_type, background)


    def render(self, content: Any) -> bytes:
        if content is None:
            return b""
        
        if self.media_type == "application/json":
            content = json.dumps(
                content,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            )
            return content.encode(self.charset)

        if self.media_type == "application/xml":
            return dicttoxml(obj=content, custom_root=self.custom_root)

class CustomRequest(Request):
    def __init__(self, scope: Scope, receive: Receive = ..., send: Send = ...):
        super().__init__(scope, receive, send)

    async def body(self):
        data = await super().body()
        content_type = self.headers.get('Content-Type')
        
        if content_type == "application/xml":
            content = xmltodict.parse(data)
            data = content[list(content.keys())[0]]

        return data

class CustomRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = CustomRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler
