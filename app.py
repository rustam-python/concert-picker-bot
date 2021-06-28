import bot
import database
import settings

database.initialize_data_base()
settings.check_config_integrity()
bot.Bot().start()
