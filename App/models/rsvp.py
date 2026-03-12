from App.database import db


class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    status = db.Column(db.String(64), nullable=True)

    user = db.relationship('User', back_populates='rsvps')
    session = db.relationship('Session', back_populates='rsvps')
