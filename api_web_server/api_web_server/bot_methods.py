import json
import time
from datetime import datetime
from typing import List, Dict, Union

import peewee
import requests
from telebot import TeleBot

from Models import Events
from Models import Places
from settings import Server


class BotMethods:
    def start_bot(self):
        while True:
            bot = TeleBot(Server.telegram_token)
            try:
                data_from_db = self.get_not_sent_events()
                if data_from_db:
                    messages = self.get_and_send_message(bot_instance=bot, events=data_from_db)
                    if messages:
                        [print(message) for message in messages]
            except Exception as err:
                print(err)
            time.sleep(3600)

    def get_and_send_message(self, bot_instance: TeleBot, events: List[Dict[str, Union[str, datetime, bool]]])\
            -> List[str]:
        if events:
            result = []
            for n, event in enumerate(events, start=1):
                try:
                    message = f'{n}. *{event["title"]}*:\n{event["date"]} в {event["name"]}({event["address"]})' \
                              f' -- билеты {event["price"]})'
                    bot_instance.send_message(149017157, f'\U0001F3B8 *Новые концерты*\n\n{message}',
                                              parse_mode='Markdown')
                    time.sleep(1)
                    result_q = Events.update({Events.message_sent: True}).where(Events.id == event['id']).execute()
                    if result_q == 0:
                        raise peewee.DataError('No rows has been updated; may be an internal problem')

                    result.append(f'{datetime.now()} --- Event "{event["id"]}" has been successfully sent.')

                except peewee.DataError as err:
                    result.append(f'{datetime.now()} --- There is an error for "{event["id"]}" row: "{str(err).strip()}".')
                except peewee.ProgrammingError as err:
                    result.append(f'{datetime.now()} --- There is an error for "{event["id"]}" row: "{str(err).strip()}".')

                except requests.exceptions.ConnectionError as err:
                    result.append(f'{datetime.now()} --- There is an error for "{event["id"]}" row: "{str(err).strip()}".')

                except KeyError as err:
                    result.append(f'{datetime.now()} --- There is no "{err}" value in "{event["id"]}" row.')

                except Exception as err:
                    result.append(f'{datetime.now()} --- {err}')

            return result
        else:
            return [f'{datetime.now()} --- There are no new data.']

        # for chunk in range(0, len(data), 10):
        #     messages = data[chunk:chunk + 10]
        #     frmt_msg = '\n\n'.join(messages)
        #     try:
        #         bot.send_message(149017157, f'\U0001F3B8 *Новые концерты*\n\n{frmt_msg}', parse_mode='Markdown')
        #     except Exception as err:
        #         print(err)

    def get_reference_from_api(self) -> Union[dict, None]:
        try:
            result = requests.get(f'http://{Server.host}:{Server.port}/get_reference')
            json_result = result.json()
            if not json_result:
                return None
            return json_result
        except requests.exceptions.ConnectionError as err:
            print(f'{datetime.now()} --- There is an error: "{str(err).strip()}".')
            raise requests.exceptions.ConnectionError(f'{datetime.now()} --- There is an error: "{str(err).strip()}".')
        except json.decoder.JSONDecodeError as err:
            print(f'{datetime.now()} --- There is an error: "{str(err).strip()}".')
            raise requests.exceptions.ConnectionError(f'{datetime.now()} --- There is an error: "{str(err).strip()}".')

    def get_not_sent_events(self) -> Union[List[Dict[str, Union[str, datetime, bool]]], None]:
        try:
            db_request = Events.select(Events.id,
                                       Events.title,
                                       Events.date,
                                       Events.price,
                                       Events.slug,
                                       Places.place_id.alias('p_id'),
                                       Places.name,
                                       Places.address). \
                join(Places, on=(Events.place_id == Places.place_id)). \
                where(Events.message_sent == False). \
                order_by(Events.date).dicts(). \
                execute()
            events = [event for event in db_request]
            if not events:
                return None
            return events
        except peewee.ProgrammingError as err:
            print(f'{datetime.now()} --- There an is error: "{str(err).strip()}".')
            raise requests.exceptions.ConnectionError(f'{datetime.now()} --- There is an error: "{str(err).strip()}".')


# if __name__ == '__main__':

