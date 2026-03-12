from App.database import db


class Award(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(200), nullable=True)

    presentations = db.relationship('Presentation', back_populates='award', lazy='dynamic')
