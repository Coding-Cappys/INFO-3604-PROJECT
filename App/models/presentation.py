from enum import Enum

from App.database import db


class PresentationType(Enum):
    Oral = "Oral"
    Poster = "Poster"


class PresentationStatus(Enum):
    Approved = "Approved"
    Scheduled = "Scheduled"
    Presented = "Presented"
    Scored = "Scored"
    AwardWinner = "AwardWinner"


class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
    type = db.Column(db.Enum(PresentationType, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    status = db.Column(db.Enum(PresentationStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=PresentationStatus.Approved)
    poster_location = db.Column(db.String(128), nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    award_id = db.Column(db.Integer, db.ForeignKey('award.id'), nullable=True)

    submission = db.relationship('Submission', back_populates='presentation')
    session = db.relationship('Session', back_populates='presentations')
    judge_assignments = db.relationship('JudgeAssignment', back_populates='presentation', lazy='dynamic')
    award = db.relationship('Award', back_populates='presentations')
