from datetime import datetime

from App.database import db


class SubmissionVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False, default=1)
    abstract = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    revision_notes = db.Column(db.Text, nullable=True)

    submission = db.relationship('Submission', back_populates='versions')
    supplementary_materials = db.relationship('SupplementaryMaterial', back_populates='submission_version', lazy='dynamic')
