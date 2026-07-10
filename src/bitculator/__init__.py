"""Official Python SDK for the Bitculator Data API."""

from ._http import Quota
from ._version import __version__
from .client import Bitculator
from .errors import (
    APIConnectionError,
    APIDecodeError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    BitculatorError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .pagination import Page

__all__ = [
    "Bitculator",
    "Page",
    "Quota",
    "BitculatorError",
    "APIError",
    "APITimeoutError",
    "APIConnectionError",
    "APIDecodeError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "__version__",
]
