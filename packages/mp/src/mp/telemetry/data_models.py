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


from datetime import datetime
from typing import Any


class TelemetryPayload:
    """A data container for a single telemetry event.

    Attributes:
        install_id: The anonymous, persistent user installation ID.
        tool: The name of the CLI tool.
        tool_version: The semantic version of the tool.
        python_version: The version of the Python interpreter.
        platform: The platform identifier (e.g., OS, architecture).
        command: The name of the command that was run.
        command_args: The arguments passed to the command.
        duration_ms: The total execution time of the command in milliseconds.
        success: True if the command exited with code 0, False otherwise.
        error_type: The Python exception class name, if an error occurred.
        stack: A trimmed stack trace, if an error occurred.
        timestamp: The UTC timestamp of when the event was generated.

    """

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        install_id: str,
        tool: str,
        tool_version: str,
        python_version: str,
        platform: str,
        platform_version: str,
        command: str,
        command_args: dict[str, Any],
        duration_ms: int,
        success: bool,  # noqa: FBT001
        error_type: str | None,
        stack: str | None,
        timestamp: datetime,
    ) -> None:
        self.install_id = install_id
        self.tool = tool
        self.tool_version = tool_version
        self.python_version = python_version
        self.platform = platform
        self.platform_version = platform_version
        self.command = command
        self.command_args = command_args
        self.duration_ms = duration_ms
        self.success = success
        self.error_type = error_type
        self.stack = stack
        self.timestamp = timestamp

    def to_dict(self) -> dict[str, Any]:
        """Serialize the event payload into a dictionary.

        This method converts the object's attributes into a dictionary format
        that is ready for JSON serialization, including formatting the timestamp
        to the required RFC3339 UTC string format.

        Returns:
            A dictionary representation of the event payload.

        """
        return {
            "install_id": self.install_id,
            "tool": self.tool,
            "tool_version": self.tool_version,
            "python_version": self.python_version,
            "platform": self.platform,
            "platform_version": self.platform_version,
            "command": self.command,
            "command_args": self.command_args,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "error_type": self.error_type,
            "stack": self.stack,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
        }
