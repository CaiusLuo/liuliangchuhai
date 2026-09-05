class AssistantError(Exception):
    """Application-visible assistant failure, independent of provider mechanics."""


class AssistantUnavailable(AssistantError):
    """The assistant service could not complete the request."""


class InvalidAssistantResponse(AssistantError):
    """The assistant returned malformed or invalid structured output."""
