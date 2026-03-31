from enum import Enum

from werkzeug.security import check_password_hash, generate_password_hash

from App.database import db


class Role(Enum):
    Admin = "Admin"
    Author = "Author"
    Reviewer = "Reviewer"
    Attendee = "Attendee"
    Judge = "Judge"
    Usher = "Usher"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True, unique=True)
    role = db.Column(
        db.Enum(Role, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=Role.Attendee,
    )
    affiliation = db.Column(db.String(256), nullable=True)
    discipline = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    checked_in = db.Column(db.Boolean, default=False)

    submissions = db.relationship("Submission", back_populates="creator")
    submission_authors = db.relationship("SubmissionAuthor", back_populates="user")
    review_submissions = db.relationship("ReviewSubmission", back_populates="reviewer")
    judge_assignments = db.relationship("JudgeAssignment", back_populates="judge")
    rsvps = db.relationship("RSVP", back_populates="user")
    attendances = db.relationship("Attendance", back_populates="user")
    feedbacks = db.relationship("Feedback", back_populates="user")
    qr_code = db.relationship("QRCode", back_populates="user", uselist=False)
    ushered_sessions = db.relationship("Session", secondary="session_ushers", back_populates="ushers")
    chaired_sessions = db.relationship("Session", foreign_keys="Session.chair_id", back_populates="chair")

    def __init__(self, username, password, **kwargs):
        self.username = username
        self.set_password(password)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_json(self):
        return {"id": self.id, "username": self.username}

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
