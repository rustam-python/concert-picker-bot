import typing

import sentry_sdk
import sentry_sdk.utils
from sentry_sdk.integrations import Integration

import logger
import settings

sentry_sdk.utils.MAX_STRING_LENGTH = 10000


# noinspection PyBroadException
def initialize_sentry(integrations: typing.Optional[list[Integration]] = None) -> None:
    """Initialize Sentry SDK Integration."""
    # TODO Add release information
    release = '1.0.0'
    _logger = logger.Logger(name='Sentry')
    try:
        sentry_sdk.init(
            dsn=settings.App.sentry_url,
            integrations=integrations if integrations else [],
            traces_sample_rate=1.0,
            release=release,
            server_name=settings.App.name,
            send_default_pii=True,
        )

    except Exception as e:
        _logger.failure(f'Sentry is failed to initialize: {e}', stack_info=True)


def capture_exception(*args, **kwargs):
    """Wrapper for sentry_sdk.capture_exception"""
    return sentry_sdk.capture_exception(*args, **kwargs)


def capture_message(*args, **kwargs):
    """Wrapper for sentry_sdk.capture_message"""
    return sentry_sdk.capture_message(*args, **kwargs)
