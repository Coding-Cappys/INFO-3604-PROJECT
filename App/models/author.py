from App.database import db


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    hashed_password = db.Column(db.String(256), nullable=False)
    affiliation = db.Column(db.String(256), nullable=False)
    discipline = db.Column(db.String(256), nullable=True)
    research_area = db.Column(db.String(256), nullable=True)
    contact_info = db.Column(db.String(256), nullable=True)
 
    submissions = db.relationship('AuthorSubmission', back_populates='author', lazy='dynamic')