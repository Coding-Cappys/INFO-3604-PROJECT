from datetime import datetime

from App.database import db


class SupplementaryMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_version_id = db.Column(db.Integer, db.ForeignKey('submission_version.id'), nullable=False)
    file_name = db.Column(db.String(256), nullable=False)
    file_type = db.Column(db.String(128), nullable=True)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    submission_version = db.relationship('SubmissionVersion', back_populates='supplementary_materials')
