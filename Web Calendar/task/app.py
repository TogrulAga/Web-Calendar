from flask import Flask, abort, request
from flask_restful import Resource, Api, inputs, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import sys
from datetime import datetime


resource_fields = {
    'id':   fields.Integer,
    'event':    fields.String,
    'date':     fields.DateTime(dt_format="iso8601"),
    'uri':      fields.Url('eventresource')
}

response_message = {
    'message':   fields.String
}


class EventsResponse:
    def __init__(self, id=None, event=None, date=None, message=None):
        self.id = id
        self.event = event
        self.date = date
        self.message = message

        self.status = "active"


class EventTodayResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        events = Event.query.all()
        response = []
        for event in events:
            if event.date == datetime.now().date():
                response.append(EventsResponse(event.id, event.event, event.date))
        return response


class EventResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        response = []
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time is None or end_time is None:
            events = Event.query.all()
        else:
            events = Event.query.filter(Event.date.between(start_time, end_time)).all()
        for event in events:
            response.append(EventsResponse(event.id, event.event, event.date))

        return response

    def post(self):
        args = parser.parse_args()
        db.session.add(Event(event=args["event"], date=args["date"]))
        db.session.commit()
        return {"message": "The event has been added!", "event": args["event"], "date": args["date"].strftime("%Y-%m-%d")}


class EventByID(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return EventsResponse(event.id, event.event, event.date)

    @marshal_with(response_message)
    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        print(event, flush=True)
        db.session.delete(event)
        db.session.commit()

        return EventsResponse(message="The event has been deleted!")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event.db'
api = Api(app)

api.add_resource(EventResource, "/event")
api.add_resource(EventTodayResource, "/event/today")
api.add_resource(EventByID, '/event/<int:event_id>')
db = SQLAlchemy(app)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()


parser = reqparse.RequestParser()

parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)

parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)

parser.add_argument(
    'start_time',
    type=inputs.date,
    required=False
)

parser.add_argument(
    'end_time',
    type=inputs.date,
    required=False
)

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
