class DigitalHumanError(Exception):
    """Base application-visible digital-human failure, independent of providers."""


class DigitalHumanUnavailable(DigitalHumanError):
    """Provider, network, quota, auth or service availability prevents completion."""


class DigitalHumanRejected(DigitalHumanError):
    """Provider rejects validated input due to unsupported, policy or input constraints."""


class InvalidDigitalHumanResponse(DigitalHumanError):
    """Provider success, state or data cannot be mapped safely to the contract."""


class DigitalHumanDeadlineExceeded(DigitalHumanError):
    """Local bounded wait ended without a known terminal remote result.

    This does not imply remote cancellation; callers must not blindly duplicate generation.
    """
