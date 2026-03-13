from datetime import datetime

from App.database import db


class JudgeAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judge_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    judge = db.relationship('User', back_populates='judge_assignments')
    presentation = db.relationship('Presentation', back_populates='judge_assignments')
    score = db.relationship('Score', back_populates='judge_assignment', uselist=False)
