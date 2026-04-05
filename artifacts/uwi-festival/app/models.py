from datetime import datetime
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    affiliation = db.Column(db.String(255))
    discipline = db.Column(db.String(255))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code = db.Column(db.Text)

    submissions = db.relationship("Submission", backref="author", lazy=True, foreign_keys="Submission.author_id")
    reviews = db.relationship("Review", backref="reviewer", lazy=True, foreign_keys="Review.reviewer_id")
    judging_scores = db.relationship("JudgingScore", backref="judge", lazy=True, foreign_keys="JudgingScore.judge_id")
    rsvps = db.relationship("RSVP", backref="attendee", lazy=True)
    session_assignments = db.relationship("UsherAssignment", backref="usher", lazy=True)
    attendances = db.relationship("AttendanceRecord", backref="checked_in_user", lazy=True, foreign_keys="AttendanceRecord.attendee_id")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User {self.email}>"


class Track(db.Model):
    __tablename__ = "tracks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    submissions = db.relationship("Submission", backref="track", lazy=True)


class Submission(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.String(500), nullable=False)
    affiliation = db.Column(db.String(500))
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(500))
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"))
    presentation_type = db.Column(db.String(50), default="oral")
    status = db.Column(db.String(50), default="submitted")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    revision_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = db.relationship("Review", backref="submission", lazy=True)
    scheduled_session = db.relationship("ScheduledSession", backref="submission", uselist=False)
    judging_scores = db.relationship("JudgingScore", backref="submission", lazy=True)
    reviewer_assignments = db.relationship("ReviewerAssignment", backref="submission", lazy=True)

    STATUS_LABELS = {
        "draft": "Draft",
        "submitted": "Submitted",
        "under_review": "Under Review",
        "changes_requested": "Changes Requested",
        "accepted": "Accepted",
        "accepted_oral": "Accepted (Oral)",
        "accepted_poster": "Accepted (Poster)",
        "rejected": "Rejected",
        "scheduled": "Scheduled",
        "resubmitted": "Resubmitted",
    }

    STATUS_COLORS = {
        "draft": "secondary",
        "submitted": "primary",
        "under_review": "warning",
        "changes_requested": "warning",
        "accepted": "success",
        "accepted_oral": "success",
        "accepted_poster": "success",
        "rejected": "danger",
        "scheduled": "info",
        "resubmitted": "primary",
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status.replace("_", " ").title())

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, "secondary")

    @property
    def average_score(self):
        if not self.reviews:
            return None
        scores = [r.overall_score for r in self.reviews if r.overall_score is not None]
        return round(sum(scores) / len(scores), 1) if scores else None


class ReviewerAssignment(db.Model):
    __tablename__ = "reviewer_assignments"
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False)
    assigned_theme = db.Column(db.String(255))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviewer = db.relationship("User", foreign_keys=[reviewer_id])


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    research_quality = db.Column(db.Integer)
    methodology = db.Column(db.Integer)
    relevance = db.Column(db.Integer)
    clarity = db.Column(db.Integer)
    overall_score = db.Column(db.Integer)
    comments = db.Column(db.Text)
    recommendation = db.Column(db.String(50))
    status = db.Column(db.String(50), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    RECOMMENDATION_LABELS = {
        "accept": "Accept",
        "accept_oral": "Accept (Oral)",
        "accept_poster": "Accept (Poster)",
        "minor_revisions": "Request Minor Revisions",
        "major_revisions": "Request Major Revisions",
        "reject": "Reject",
    }

    @property
    def recommendation_label(self):
        return self.RECOMMENDATION_LABELS.get(self.recommendation, self.recommendation or "Pending")


class Venue(db.Model):
    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(500))
    capacity = db.Column(db.Integer)
    sessions = db.relationship("ScheduledSession", backref="venue", lazy=True)


class ScheduledSession(db.Model):
    __tablename__ = "scheduled_sessions"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"))
    session_date = db.Column(db.String(20))
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    session_chair = db.Column(db.String(255))
    poster_board = db.Column(db.String(20))

    usher_assignments = db.relationship("UsherAssignment", backref="session", lazy=True)
    rsvps = db.relationship("RSVP", backref="session", lazy=True)
    attendance_records = db.relationship("AttendanceRecord", backref="session", lazy=True)
    feedback = db.relationship("SessionFeedback", backref="session", lazy=True)


class JudgingScore(db.Model):
    __tablename__ = "judging_scores"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False)
    judge_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    research_quality = db.Column(db.Integer)
    clarity = db.Column(db.Integer)
    innovation = db.Column(db.Integer)
    response_to_questions = db.Column(db.Integer)
    overall_impact = db.Column(db.Integer)
    comments = db.Column(db.Text)
    status = db.Column(db.String(50), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def total_score(self):
        scores = [self.research_quality, self.clarity, self.innovation,
                  self.response_to_questions, self.overall_impact]
        valid = [s for s in scores if s is not None]
        return round(sum(valid) / len(valid), 1) if valid else None


class RSVP(db.Model):
    __tablename__ = "rsvps"
    id = db.Column(db.Integer, primary_key=True)
    attendee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("scheduled_sessions.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("attendee_id", "session_id"),)


class SessionFeedback(db.Model):
    __tablename__ = "session_feedback"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("scheduled_sessions.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content_quality = db.Column(db.Integer)
    presentation_effectiveness = db.Column(db.Integer)
    relevance = db.Column(db.Integer)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("scheduled_sessions.id"), nullable=False)
    attendee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    usher_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    checked_in_at = db.Column(db.DateTime, default=datetime.utcnow)
    method = db.Column(db.String(20), default="manual")
    attendee = db.relationship("User", foreign_keys=[attendee_id], overlaps="attendances,checked_in_user")
    __table_args__ = (db.UniqueConstraint("session_id", "attendee_id"),)


class UsherAssignment(db.Model):
    __tablename__ = "usher_assignments"
    id = db.Column(db.Integer, primary_key=True)
    usher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("scheduled_sessions.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
