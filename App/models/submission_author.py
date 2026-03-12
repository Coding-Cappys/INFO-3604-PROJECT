from App.database import db


class SubmissionAuthor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_order = db.Column(db.Integer, nullable=False, default=0)
    is_corresponding = db.Column(db.Boolean, nullable=False, default=False)

    submission = db.relationship('Submission', back_populates='authors')
    user = db.relationship('User', back_populates='submission_authors')
