# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import aiohttp
import aiohttp.base_protocol
from TIPCommon.utils import none_to_default_value
from yarl import URL

if TYPE_CHECKING:
    from TIPCommon.types import JSON, JsonString, SingleJson


class MockClientResponse(aiohttp.ClientResponse):
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        content: str | JsonString | JSON = "",
        status_code: int = 200,
        encoding: str = "UTF-8",
        headers: SingleJson | None = None,
        method: str = "",
        url: str = "",
    ) -> None:
        super().__init__(
            method=method,
            url=URL(url),
            writer=None,
            continue100=None,
            timer=None,
            request_info=None,
            traces=None,
            session=None,
            loop=asyncio.get_event_loop(),
        )
        self.content = aiohttp.streams.StreamReader(
            aiohttp.base_protocol.BaseProtocol(asyncio.get_event_loop()),
            2**16,
        )
        self.content.feed_data(_stringify_content(content).encode(encoding))
        self.content.feed_eof()
        self.status: int = status_code
        self.encoding: str = encoding
        self._headers: SingleJson = none_to_default_value(headers, {})
        self._traces = []
        self.reason = "Some very valid reason"

    def __repr__(self) -> str:
        return (
            f"{MockClientResponse.__name__}("
            f"status_code={self.status}, "
            f"content={self.content}, "
            f"encoding={self.encoding}, "
            f"headers={self.headers}"
            ")"
        )


def _stringify_content(content: JSON | JsonString | str) -> JsonString:
    if not isinstance(content, str):
        return json.dumps(content)

    return content
