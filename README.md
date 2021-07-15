# Concert picker bot
 [![codecov](https://codecov.io/gh/rustam-python/Concert-picker-bot/branch/master/graph/badge.svg)](https://codecov.io/gh/rustam-python/Concert-picker-bot)    [![Build Status](https://travis-ci.org/rustam-python/Concert-picker-bot.svg?branch=Developing)](https://travis-ci.org/rustam-python/Concert-picker-bot)

A Telegram bot designed for concert searching based on requests to API of kudago.сom (as concert data source) and the Last.FM (as statistics data source).

## :wrench: Dependencies and Installation
* Python >= 3.7
* SQLite3
* pyTelegramBotAPI==3.8.1
* peewee==3.14.4
* requests==2.26.0
* aiohttp>=3.7.4
* pydantic==1.8.2
* aiohttp>=3.7.4
* pytz==2021.1
* ConfigORM==0.1.0

These instructions will get you a copy of the Concert picker bot up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Installation
1. Clone repo
```console
$ git clone https://github.com/rustam-python/Concert-picker-bot.git
$ cd Concert-picker-bot
```
2. Create `venv`:
```console
$ virtualenv --python=/usr/bin/python38 venv
$ source venv/bin/activate
```
3. Install dependent packages:
```console
(venv)$ pip install -r requirements.txt
```
### Settings
The application uses configuration file `cbp-config.ini`. To use the application your way, you need to create in the following configuration file (or just start the app - it will create automatically in `settings/`):
```ini
[APIs]
;KudaGo API URL
kudago_url = https://kudago.com/public-api/v1.4/events/?lang=&page_size=100&fields=id,dates,title,place,slug,price&expand=&order_by=&text_format=&ids=&location=msk&actual_since={}&actual_until=&is_free=&categories=concert

;LastFM API URL
lastfm_url = http://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={}&period=overall&limit={}&api_key={}&format=json

lastfm_username = your_last_fm_username
lastfm_token = your_last_fm_key
lastfm_artists_limit = 300 ;how many scrobbled artists will be returned
telegram_token = your_tg_key
telegram_chat_id=your_tg_chat_id

[DataBase]
; If you are using SQLite just leave it empty.
username
password
host
name
transaction_retry_limit = 5
bunch_size = 1000

[App]
; APIs request interval.
delay_time = 3600

```

### Starting

Start app manually:

```console
(venv)$ python3 app.py
```
* For the correct running of the application, it is necessary to provide access from your local system to https://api.telegram.org.
