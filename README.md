# Concert picker bot

A Telegram bot for concert searching based on requests to API of kudago.сom (as concert data source) and the Last.FM (as statistics data source).

## Getting Started
Getting Started
These instructions will get you a copy of the Concert picker bot up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
What things you need to deploy the Concert picker bot on your system:

1. [Docker Engine-Community](https://docs.docker.com/install/linux/docker-ce/centos/) — any flavor you preffer (or for Windows).

2. [Docker Compose](https://docs.docker.com/compose/install/) — as simple orchestrator.


### Modules
The bot uses the following modules:
1. NGINX as a reverse proxy (for access to the graphical API of the web server).
2. PostgreSQL database for storing cumulative data.
3. The web server on gevent.pywsgi as the API server.
4. Container with telegram bot appication. *

* Please note that in order to save valuable AWS instance disk space, the web server and telegram bot containers use the same image. If necessary, you can separate them as you wish.

### Settings
The application uses configuration files to interact with user configurations. To use the application your way, you need to create in the following configuration files:
1. variables.env — is settings file for postgres container.

```
POSTGRES_DB_HOST_NAME=db_host
POSTGRES_DB_PORT=db_port
POSTGRES_DB=db_name
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```
2. api-web-server-config.ini — is settings file of web server. Add your DB settings, LastFM API key and Telegram token.
```
[Database]
host = db_host
port = db_port
base = db_name
username = user
password = password

[Server]
host = 0.0.0.0
port = 5005
last_fm_api_key = key
telegram_token = token

```

### Deploying

Build the containers and start docker-compose:

```
cd path_to_cloned_project/
docker-compose build
docker-compose up -d
```
* For the correct running of the application, it is necessary to provide access from your local system to https://api.telegram.org.
