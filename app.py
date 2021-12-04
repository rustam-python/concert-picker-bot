import database
import sentry
import settings
import threads
from sentry_sdk.integrations.redis import RedisIntegration


sentry.initialize_sentry(integrations=[RedisIntegration()])
database.initialize_data_base(is_local=False)
settings.check_config_integrity()
for thread in (threads.ThreadHolder.get_bot_thread(), threads.ThreadHolder.get_lastfm_data_thread()):
    thread.join()
