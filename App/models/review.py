from enum import Enum
from datetime import datetime

from App.database import db


class ReviewDecision(Enum):
    Approve = "Approve"
    RequestChanges = "RequestChanges"
    RecommendPoster = "RecommendPoster"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_assignment_id = db.Column(db.Integer, db.ForeignKey('review_assignment.id'), nullable=False)
    decision = db.Column(db.Enum(ReviewDecision, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    assignment = db.relationship('ReviewAssignment', back_populates='review')
