from flask import Flask, jsonify
from flask_restplus import Resource, Api
from gevent.pywsgi import WSGIServer

from events_processor import EventsProcessor
from Models import BaseModel, Events
from settings import Server

BaseModel.recreate_tables()

app = Flask(__name__)
api = Api(app)


@api.route('/get_reference')
class ReferenceGrabber(Resource):
    def get(self):
        events_instance = EventsProcessor()
        events = events_instance.process()
        if not events:
            return jsonify({'Result': 'No new data'})
        else:
            return jsonify({'Result': events_instance.events_list})


@api.route('/get_messages')
class MessagesGetter(Resource):
    def get(self):
        events = [event for event in Events.select(Events.title, Events.date, Events.message_sent).dicts().execute()]
        if not events:
            return jsonify({'Result': 'No events data'})
        else:
            return jsonify({'Result': events})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5005)


http_server = WSGIServer((Server.host, Server.port), app)
http_server.serve_forever()
