from App.database import db


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.Text, nullable=True)

    user = db.relationship('User', back_populates='feedbacks')
    session = db.relationship('Session', back_populates='feedbacks')
