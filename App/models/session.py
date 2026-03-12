from App.database import db

# Association table for many-to-many relationship between Session and User (ushers)
session_ushers = db.Table(
    'session_ushers',
    db.Column('session_id', db.Integer, db.ForeignKey('session.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    date = db.Column(db.Date, nullable=True)
    time_slot = db.Column(db.String(128), nullable=True)
    venue = db.Column(db.String(256), nullable=True)

    track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=True)
    chair_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    track = db.relationship('Track', back_populates='sessions')
    chair = db.relationship('User', foreign_keys=[chair_id])
    ushers = db.relationship('User', secondary=session_ushers, backref='ushered_sessions')

    presentations = db.relationship('Presentation', back_populates='session', lazy='dynamic')
    rsvps = db.relationship('RSVP', back_populates='session', lazy='dynamic')
    attendances = db.relationship('Attendance', back_populates='session', lazy='dynamic')
    feedbacks = db.relationship('Feedback', back_populates='session', lazy='dynamic')
