from datetime import datetime

from App.database import db


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='attendances')
    session = db.relationship('Session', back_populates='attendances')
