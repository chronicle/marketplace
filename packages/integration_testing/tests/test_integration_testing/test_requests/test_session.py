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

import secrets
import urllib.parse
import uuid

from integration_testing import router
from integration_testing.common import get_empty_response
from integration_testing.request import HttpMethod, MockRequest
from integration_testing.requests.response import MockResponse
from integration_testing.requests.session import MockSession, RouteFunction


class TestInitialization:
    def test_initialization_with_no_parameters(self) -> None:
        session: MockSession = MockSession()

        assert session is not None

    def test_initialization_with_parameters(self) -> None:
        product: MockProduct = MockProduct()
        session: MockSession = MockSession(product)

        assert session is not None


class TestSessionRequests:
    def test_number_of_requests_equals_number_of_records(
        self,
        url: str,
        parsed_url: urllib.parse.ParseResult,
        session: MockSession,
    ) -> None:
        session.routes[HttpMethod.GET.value][parsed_url.path] = get_empty_response
        test_range: int = 10
        for _ in range(test_range):
            num_of_requests: int = secrets.randbelow(exclusive_upper_bound=test_range)
            for _ in range(num_of_requests):
                session.get(url)

            number_of_requests_in_record: int = len(session.request_history)

            assert number_of_requests_in_record == num_of_requests

            session.clear_record()

    def test_get_request_is_added_to_record(
        self,
        url: str,
        parsed_url: urllib.parse.ParseResult,
        session: MockSession,
    ) -> None:
        session.routes[HttpMethod.GET.value][parsed_url.path] = get_empty_response

        session.get(url)
        request: MockRequest = session.request_history[0].request
        response: MockResponse = session.request_history[0].response

        assert request.method == HttpMethod.GET
        assert request.url == parsed_url
        assert isinstance(response, MockResponse)

    def test_delete_request_is_added_to_record(
        self,
        url: str,
        parsed_url: urllib.parse.ParseResult,
        session: MockSession,
    ) -> None:
        session.routes[HttpMethod.DELETE.value][parsed_url.path] = get_empty_response

        session.delete(url)
        request: MockRequest = session.request_history[0].request
        response: MockResponse = session.request_history[0].response

        assert request.method == HttpMethod.DELETE
        assert request.url == parsed_url
        assert isinstance(response, MockResponse)

    def test_post_request_is_added_to_record(
        self,
        url: str,
        parsed_url: urllib.parse.ParseResult,
        session: MockSession,
    ) -> None:
        session.routes[HttpMethod.POST.value][parsed_url.path] = get_empty_response

        session.post(url)
        request: MockRequest = session.request_history[0].request
        response: MockResponse = session.request_history[0].response

        assert request.method == HttpMethod.POST
        assert request.url == parsed_url
        assert isinstance(response, MockResponse)

    def test_put_request_is_added_to_record(
        self,
        url: str,
        parsed_url: urllib.parse.ParseResult,
        session: MockSession,
    ) -> None:
        session.routes[HttpMethod.PUT.value][parsed_url.path] = get_empty_response

        session.put(url)
        request: MockRequest = session.request_history[0].request
        response: MockResponse = session.request_history[0].response

        assert request.method == HttpMethod.PUT
        assert request.url == parsed_url
        assert isinstance(response, MockResponse)

    def test_patch_request_is_added_to_record(
        self,
        url: str,
        parsed_url: urllib.parse.ParseResult,
        session: MockSession,
    ) -> None:
        session.routes[HttpMethod.PATCH.value][parsed_url.path] = get_empty_response

        session.patch(url)
        request: MockRequest = session.request_history[0].request
        response: MockResponse = session.request_history[0].response

        assert request.method == HttpMethod.PATCH
        assert request.url == parsed_url
        assert isinstance(response, MockResponse)

    def test_get_request_matches_with_regex(self, session: MockSession) -> None:
        ticket_id = str(uuid.uuid4())
        url: str = f"https://localhost:1111/api/v1/ticket/id/{ticket_id}"
        parsed_url: urllib.parse.ParseResult = urllib.parse.urlparse(url)
        session.routes[HttpMethod.PATCH.value][r"/api/v1/ticket/id/[a-z0-9\-]+"] = (
            get_empty_response
        )

        session.patch(url)
        request: MockRequest = session.request_history[0].request
        response: MockResponse = session.request_history[0].response

        assert request.method == HttpMethod.PATCH
        assert request.url == parsed_url
        assert isinstance(response, MockResponse)

    def test_similar_routs_are_matched(self, session: MockSession) -> None:
        url_1: str = "https://localhost:1111/api/v1/ticket"
        url_2: str = "https://localhost:1111/api/v1/ticket/id"
        parsed_url_1: urllib.parse.ParseResult = urllib.parse.urlparse(url_1)
        parsed_url_2: urllib.parse.ParseResult = urllib.parse.urlparse(url_2)
        session.routes[HttpMethod.PATCH.value]["/api/v1/ticket"] = get_empty_response
        session.routes[HttpMethod.PATCH.value]["/api/v1/ticket/id"] = get_empty_response

        session.patch(url_1)
        session.patch(url_2)
        request_1: MockRequest = session.request_history[0].request
        request_2: MockRequest = session.request_history[1].request
        response_1: MockResponse = session.request_history[0].response
        response_2: MockResponse = session.request_history[1].response

        assert request_1.method == HttpMethod.PATCH
        assert request_2.method == HttpMethod.PATCH
        assert request_1.url == parsed_url_1
        assert request_2.url == parsed_url_2
        assert isinstance(response_1, MockResponse)
        assert isinstance(response_2, MockResponse)

    def test_get_routes_add_routes_to_session_routes(self, url: str) -> None:
        @router.get(url)
        def do_request() -> MockResponse:
            return MockResponse()

        class CustomSession(MockSession[MockRequest, MockResponse, None]):
            def get_routed_functions(self) -> list[RouteFunction]:
                return [do_request]

        session: CustomSession = CustomSession()

        assert session.routes[HttpMethod.GET.value][url] is do_request
