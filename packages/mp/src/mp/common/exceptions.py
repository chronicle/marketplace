class FatalException(Exception):
    """Base class for exceptions that should cause the program to crash."""

    def __init__(self, message: str = "A fatal error occurred, program will terminate."):
        super().__init__(message)
        self.message = message


class NonFatalException(Exception):
    """Base class for exceptions that should not cause the program to crash."""

    def __init__(self, message: str = "A non fatal error occurred."):
        super().__init__(message)
        self.message = message


class CommandErrors(NonFatalException):
    """Error that happens during shell commands."""
