from enum import Enum
from datetime import datetime

from App.database import db


class SubmissionStatus(Enum):
    Draft = "Draft"
    Submitted = "Submitted"
    UnderReview = "UnderReview"
    ChangesRequested = "ChangesRequested"
    AcceptedOral = "AcceptedOral"
    AcceptedPoster = "AcceptedPoster"
    Rejected = "Rejected"
    Scheduled = "Scheduled"


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    keywords = db.Column(db.String(512), nullable=True)
    status = db.Column(db.Enum(SubmissionStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=SubmissionStatus.Draft)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    primary_track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=True)
    secondary_track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=True)

    creator = db.relationship('User', back_populates='submissions')
    primary_track = db.relationship('Track', foreign_keys=[primary_track_id], back_populates='submissions_primary')
    secondary_track = db.relationship('Track', foreign_keys=[secondary_track_id], back_populates='submissions_secondary')

    versions = db.relationship('SubmissionVersion', back_populates='submission', lazy='dynamic')
    authors = db.relationship('SubmissionAuthor', back_populates='submission', lazy='dynamic')
    review_assignments = db.relationship('ReviewAssignment', back_populates='submission', lazy='dynamic')
    presentation = db.relationship('Presentation', back_populates='submission', uselist=False)
