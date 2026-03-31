from datetime import datetime
from enum import Enum

from App.database import db


class SubmissionStatus(Enum):
    Draft = "Draft"
    Submitted = "Submitted"
    InReview = "In Review"
    UnderReview = "In Review"
    ChangesRequested = "Changes Requested"
    AcceptedOral = "Accepted for Oral"
    AcceptedPoster = "Accepted for Poster"
    Rejected = "Rejected"
    Scheduled = "Scheduled"


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    keywords = db.Column(db.String(512), nullable=True)
    status = db.Column(
        db.Enum(SubmissionStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=SubmissionStatus.Draft,
    )
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    primary_track_id = db.Column(db.Integer, db.ForeignKey("track.id"), nullable=True)
    secondary_track_id = db.Column(db.Integer, db.ForeignKey("track.id"), nullable=True)

    creator = db.relationship("User", back_populates="submissions")
    primary_track = db.relationship("Track", foreign_keys=[primary_track_id], back_populates="primary_submissions")
    secondary_track = db.relationship("Track", foreign_keys=[secondary_track_id], back_populates="secondary_submissions")
    authors = db.relationship(
        "SubmissionAuthor",
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionAuthor.author_order",
    )
    review_submissions = db.relationship(
        "ReviewSubmission",
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="ReviewSubmission.assigned_at.desc()",
    )
    versions = db.relationship(
        "SubmissionVersion",
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionVersion.version_number.desc()",
    )
    presentation = db.relationship(
        "Presentation",
        back_populates="submission",
        uselist=False,
        cascade="all, delete-orphan",
    )
