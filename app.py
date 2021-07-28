import database
import settings
import threads

database.initialize_data_base()
settings.check_config_integrity()
threads.ThreadHolder.get_bot_thread()
