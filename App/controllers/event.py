from App.models import Event
from App import db
from datetime import date, time

def create_event(title, event_date, event_time, location, type):
    new_event = Event(
        title=title,
        date=event_date,
        time=event_time,
        location=location,
        type=type
    )
    db.session.add(new_event)
    db.session.commit()
    return new_event