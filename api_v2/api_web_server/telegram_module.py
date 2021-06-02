from telegram.error import InvalidToken, TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.ext import CommandHandler
from telegram.ext import Updater

from api_v2.api_web_server.logging_utils import get_logger

logger = get_logger('Telegram')

try:
    updater = Updater(token='TOKEN')
except InvalidToken:
    raise


def error_callback(update, context):
    try:
        raise context.error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        pass
    except BadRequest:
        # handle malformed requests - read more below!
        pass
    except TimedOut:
        # handle slow connection problems
        pass
    except NetworkError:
        # handle other connection problems
        pass
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        pass
    except TelegramError:
        # handle all other telegram related errors
        pass


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


start_handler = CommandHandler('start', start)
# Get the dispatcher to register handlers
dispatcher = updater.dispatcher
dispatcher.add_handler(start_handler)
