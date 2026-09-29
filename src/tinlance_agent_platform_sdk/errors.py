"""Stable SDK exception hierarchy mapped from the Platform HTTP contract."""

from __future__ import annotations


class SdkError(Exception):
    """Base class for all SDK-originated errors."""


class TransportError(SdkError):
    """Network or transport failure before a valid Platform response was received."""


class PlatformError(SdkError):
    """Platform returned an HTTP error or malformed success response."""

    def __init__(
        self, message: str, *, status_code: int | None = None, error_code: str | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


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
