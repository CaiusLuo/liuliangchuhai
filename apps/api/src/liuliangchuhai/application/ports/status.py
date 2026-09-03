from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderStatus:
    """Application-visible provider availability without SDK-specific details."""

    provider: str
    available: bool
