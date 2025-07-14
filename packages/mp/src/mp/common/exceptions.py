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


class FatalExceptionError(Exception):
    """Base class for exceptions that should cause the program to crash."""

    def __init__(self, message: str) -> None:  # Added -> None
        """Initialize the FatalExceptionError with a specific message.

        Args:
            message: A string describing the error.

        """
        super().__init__(message)
        self.message = message  # This line was in your original output, keeping it


class NonFatalExceptionError(Exception):
    """Base class for exceptions that should not cause the program to crash."""

    def __init__(self, message: str) -> None:  # Added -> None
        """Initialize the NonFatalExceptionError with a specific message.

        Args:
            message: A string describing the error.

        """
        super().__init__(message)
        self.message = message  # This line was in your original output, keeping it


class CommandvError(NonFatalExceptionError):
    """Error that happens during shell commands."""
