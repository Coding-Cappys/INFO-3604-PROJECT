from App.database import db


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judge_assignment_id = db.Column(db.Integer, db.ForeignKey('judge_assignment.id'), nullable=False)
    research_quality = db.Column(db.Integer, nullable=True)
    clarity = db.Column(db.Integer, nullable=True)
    innovation = db.Column(db.Integer, nullable=True)
    response_to_questions = db.Column(db.Integer, nullable=True)
    overall_impact = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.Text, nullable=True)

    judge_assignment = db.relationship('JudgeAssignment', back_populates='score')
