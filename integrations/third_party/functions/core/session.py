from typing import Iterable

from integration_testing.custom_types import RouteFunction
from integration_testing import router

from packages.integration_testing.src.integration_testing.requests.response import MockResponse
from packages.integration_testing.src.integration_testing.requests.session import MockSession, Response
from integration_testing.common import create_case_details


class MockSdkSession(MockSession):
    def get_routed_functions(self) -> Iterable[RouteFunction[Response]]:
        return [self.get_case]

    @router.get("/api/external/v1/sdk/CaseMetadata/None")
    def get_case(self) -> MockResponse:
        case_details = create_case_details(id_=1, name="asd")
        mock_response = MockResponse(
            status_code=200,
            content=case_details.to_json()
        )
        return mock_response
