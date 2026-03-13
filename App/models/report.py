from datetime import datetime

from App.database import db


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=True)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendance.id'), nullable=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)

    submission = db.relationship('Submission', foreign_keys=[submission_id])
    attendance = db.relationship('Attendance', foreign_keys=[attendance_id])
    feedback = db.relationship('Feedback', foreign_keys=[feedback_id])
