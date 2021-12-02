import database
import sentry
import settings
import threads


sentry.initialize_sentry()
database.initialize_data_base(is_local=False)
settings.check_config_integrity()
for thread in (threads.ThreadHolder.get_bot_thread(), threads.ThreadHolder.get_lastfm_data_thread()):
    thread.join()
