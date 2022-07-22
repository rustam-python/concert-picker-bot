import database
import logger
import sentry
import settings
import threads
from sentry_sdk.integrations.redis import RedisIntegration


_logger = logger.Logger(name='App')
_logger.info('App initialization started...')

sentry.initialize_sentry(integrations=[RedisIntegration()])
database.initialize_data_base(is_local=False)
settings.check_config_integrity()
threads.ThreadHolder.start_threads()
