from App.database import db


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    theme = db.Column(db.String(256), nullable=True)

    primary_submissions = db.relationship(
        "Submission",
        foreign_keys="Submission.primary_track_id",
        back_populates="primary_track",
    )
    secondary_submissions = db.relationship(
        "Submission",
        foreign_keys="Submission.secondary_track_id",
        back_populates="secondary_track",
    )
    sessions = db.relationship("Session", back_populates="track")
