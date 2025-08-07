from ..core.base_action import BaseAction
from ..core.constants import PING_SCRIPT_NAME

SUCCESS_MESSAGE = (
    "Successfully connected to the API Service server with the provided connection "
    "parameters!"
)
ERROR_MESSAGE = "Failed to connect to the API Service server!"


class Ping(BaseAction):

    def __init__(self) -> None:
        super().__init__(PING_SCRIPT_NAME)
        self.output_message = SUCCESS_MESSAGE
        self.error_output_message = ERROR_MESSAGE
        self.json_results = {}

    def _perform_action(self, _=None) -> None:
        self.api_client.test_connectivity()


def main():
    Ping().run()


if __name__ == "__main__":
    main()
