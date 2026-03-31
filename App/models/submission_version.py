from datetime import datetime

from App.database import db


class SubmissionVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submission.id"), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    revision_notes = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    submission = db.relationship("Submission", back_populates="versions")
    supplementary_materials = db.relationship(
        "SupplementaryMaterial",
        back_populates="submission_version",
        cascade="all, delete-orphan",
        order_by="SupplementaryMaterial.upload_date.desc()",
    )
