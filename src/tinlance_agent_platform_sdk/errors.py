"""Stable SDK exception hierarchy mapped from the Platform HTTP contract."""

from __future__ import annotations


class SdkError(Exception):
    """Base class for all SDK-originated errors."""


class TransportError(SdkError):
    """Network or transport failure before a valid Platform response was received."""


class PlatformError(SdkError):
    """Platform returned an HTTP error or malformed success response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        request_id: str | None = None,
        operation: str | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id
        self.operation = operation
        self.retryable = retryable

    def as_structured(self) -> dict[str, object]:
        """Return safe, machine-readable error metadata without credentials."""
        return {
            "code": self.error_code or self.__class__.__name__,
            "message": str(self),
            "status_code": self.status_code,
            "request_id": self.request_id,
            "operation": self.operation,
            "retryable": self.retryable,
        }


class AuthenticationError(PlatformError):
    """The Platform rejected the bearer credential."""


class PermissionError(PlatformError):
    """The Platform rejected the authenticated principal's authority."""


class ApiVersionError(PlatformError):
    """The Platform rejected the requested API version."""


class IdempotencyConflictError(PlatformError):
    """The request ID was previously used for a different consequential request."""


class InvalidRequestError(PlatformError):
    """The Platform rejected the request as invalid."""


class UnsupportedMediaTypeError(PlatformError):
    """The Platform rejected the request content type."""


class RequestTooLargeError(PlatformError):
    """The Platform rejected a request exceeding the size limit."""


class ExecutionError(PlatformError):
    """Structured failure from the governed-execution.v1 authority boundary."""
