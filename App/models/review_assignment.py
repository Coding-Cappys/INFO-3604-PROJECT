from datetime import datetime

from App.database import db


class ReviewAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(64), nullable=True)

    submission = db.relationship('Submission', back_populates='review_assignments')
    reviewer = db.relationship('User', back_populates='review_assignments')
    review = db.relationship('Review', back_populates='assignment', uselist=False)
