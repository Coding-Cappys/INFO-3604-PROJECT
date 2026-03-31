from App.database import db
from django.conf import settings
from enum import Enum
from datetime import datetime



class SubmissionStatus(Enum):
    Submitted = "Submitted"
    InReview = "In Review"
    NeedsRevision = "Needs Revision"
    AcceptedOral = "Accepted for Oral"
    AcceptedPoster = "Accepted for Poster"
    Rejected = "Rejected"



class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    researcher_name = db.Column(db.String(256), nullable=False)
    author_names = db.Column(db.String(512), nullable=False)
    affiliation = db.Column(db.String(256), nullable=False)
    abstract_text = db.Column(db.Text, nullable=False)
    attached_document = db.Column(db.String(512), nullable=True)
    status = db.Column(db.Enum(SubmissionStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=SubmissionStatus.Submitted)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
 
    creator = db.relationship('User', back_populates='submissions')
    authors = db.relationship('AuthorSubmission', back_populates='submission', lazy='dynamic')
    review_submissions = db.relationship('ReviewSubmission', back_populates='submission', lazy='dynamic')