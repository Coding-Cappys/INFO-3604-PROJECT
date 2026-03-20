from datetime import datetime

from App.database import db
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)

    date = db.Column(db.Date)
    time = db.Column(db.Time)
    location = db.Column(db.String(128))

    type = db.Column(db.String(50))  # "presentation", "ceremony"

    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=True)
    presentation = db.relationship('Presentation')
    rsvp = db.Column(db.Boolean, default=False) 