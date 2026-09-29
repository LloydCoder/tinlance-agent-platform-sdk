"""Public client SDK for the Tinlance Agent Platform API v1.1."""

from .async_client import AsyncAgentPlatform
from .client import AgentPlatform
from .compat import (
    DEFERRED_OPERATIONS,
    PUBLIC_OPERATIONS,
    SDK_VERSION,
    SUPPORTED_PLATFORM_API_VERSIONS,
)
from .config import ClientConfig
from .errors import (
    ApiVersionError,
    AuthenticationError,
    ExecutionError,
    IdempotencyConflictError,
    InvalidRequestError,
    PermissionError,
    PlatformError,
    RequestTooLargeError,
    SdkError,
    TransportError,
    UnsupportedMediaTypeError,
)
from .models import (
    Agent,
    ApprovalDecision,
    ApprovalRef,
    Capability,
    Event,
    EvidenceRef,
    Execution,
    Health,
    Principal,
    Run,
)
from .research import ResearchAgent, ResearchRequest, ResearchRun
from .tools import ToolContractRegistry, ToolDescriptor, ToolInvocation, ToolResult

__all__ = [
    "AgentPlatform",
    "AsyncAgentPlatform",
    "Agent",
    "ClientConfig",
    "DEFERRED_OPERATIONS",
    "ApiVersionError",
    "ApprovalDecision",
    "ApprovalRef",
    "AuthenticationError",
    "Capability",
    "Event",
    "EvidenceRef",
    "ExecutionError",
    "Execution",
    "Health",
    "IdempotencyConflictError",
    "InvalidRequestError",
    "PermissionError",
    "PlatformError",
    "Principal",
    "RequestTooLargeError",
    "Run",
    "ResearchAgent",
    "ResearchRequest",
    "ResearchRun",
    "PUBLIC_OPERATIONS",
    "SDK_VERSION",
    "SUPPORTED_PLATFORM_API_VERSIONS",
    "ToolContractRegistry",
    "ToolDescriptor",
    "ToolInvocation",
    "ToolResult",
    "SdkError",
    "TransportError",
    "UnsupportedMediaTypeError",
]
