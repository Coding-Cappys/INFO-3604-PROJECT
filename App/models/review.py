from enum import Enum
from datetime import datetime

from App.database import db


class ReviewDecision(Enum):
    ApproveOral = "ApproveOral"
    RequestChanges = "RequestChanges"
    ApprovePoster = "ApprovePoster"
    Rejected = "Rejected"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_submission_id = db.Column(db.Integer, db.ForeignKey('review_submission.id'), nullable=False, unique=True)
    decision = db.Column(db.Enum(ReviewDecision, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    attached_document = db.Column(db.String(512), nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    review_submission = db.relationship('ReviewSubmission', back_populates='review')
