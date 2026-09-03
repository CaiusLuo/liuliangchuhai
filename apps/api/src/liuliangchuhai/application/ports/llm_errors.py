class LLMError(Exception):
    """Base application-visible LLM failure, independent of provider mechanics."""


class LLMUnavailable(LLMError):
    """A future adapter maps provider timeout, outage or SDK failure to this error."""


class InvalidLLMResponse(LLMError):
    """A future adapter maps malformed or invalid structured output to this error."""
