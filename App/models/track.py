from App.database import db


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(256), nullable=True)

    submissions = db.relationship('TrackSubmission', back_populates='track', lazy='dynamic')
    reviewer = db.relationship('User', back_populates='track', lazy='dynamic')
