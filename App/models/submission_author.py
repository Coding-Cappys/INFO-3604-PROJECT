from App.database import db
from datetime import datetime


class SubmissionAuthor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    role = db.Column(db.String(128), nullable=False)
    associated_at = db.Column(db.DateTime, nullable=False, default=datetime.timezone.utcnow)
 
    author = db.relationship('Author', back_populates='submissions')
    submission = db.relationship('Submission', back_populates='authors')