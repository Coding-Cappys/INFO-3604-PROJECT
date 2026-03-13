from App.database import db


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    theme = db.Column(db.String(256), nullable=True)

    sessions = db.relationship('Session', back_populates='track', lazy='dynamic')
    submissions_primary = db.relationship('Submission', back_populates='primary_track', foreign_keys='Submission.primary_track_id', lazy='dynamic')
    submissions_secondary = db.relationship('Submission', back_populates='secondary_track', foreign_keys='Submission.secondary_track_id', lazy='dynamic')
