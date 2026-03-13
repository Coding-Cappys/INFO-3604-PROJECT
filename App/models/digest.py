from App.database import db


class Digest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.Text, nullable=True)

    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=True)
    presentation = db.relationship('Presentation', foreign_keys=[presentation_id])
