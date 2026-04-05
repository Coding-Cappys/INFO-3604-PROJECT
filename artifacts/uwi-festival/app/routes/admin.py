from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from .. import db
from ..models import (
    User, Submission, Review, ScheduledSession, Venue, Track,
    JudgingScore, ReviewerAssignment, UsherAssignment
)
from .utils import parse_int

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "total_submissions": Submission.query.count(),
        "submitted": Submission.query.filter_by(status="submitted").count(),
        "under_review": Submission.query.filter(
            Submission.status.in_(["under_review", "resubmitted"])
        ).count(),
        "accepted": Submission.query.filter(
            Submission.status.in_(["accepted", "accepted_oral", "accepted_poster"])
        ).count(),
        "rejected": Submission.query.filter_by(status="rejected").count(),
        "scheduled": Submission.query.filter_by(status="scheduled").count(),
        "total_reviews": Review.query.count(),
        "pending_reviews": Review.query.filter_by(status="draft").count(),
        "total_users": User.query.count(),
        "total_scores": JudgingScore.query.filter_by(status="submitted").count(),
    }
    recent_submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_submissions=recent_submissions)


@admin_bp.route("/submissions")
@login_required
@admin_required
def submissions():
    status_filter = request.args.get("status", "")
    track_filter = request.args.get("track", "")
    search = request.args.get("search", "")

    query = Submission.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if track_filter:
        track_id = parse_int(track_filter, minimum=1)
        if track_id is None:
            flash("Invalid track filter.", "warning")
            return redirect(url_for("admin.submissions"))
        query = query.filter_by(track_id=track_id)
    if search:
        query = query.filter(
            Submission.title.ilike(f"%{search}%") | Submission.authors.ilike(f"%{search}%")
        )
    submissions = query.order_by(Submission.submitted_at.desc()).all()
    tracks = Track.query.all()
    return render_template("admin/submissions.html", submissions=submissions, tracks=tracks,
                           status_filter=status_filter, track_filter=track_filter, search=search)


@admin_bp.route("/submissions/<int:submission_id>")
@login_required
@admin_required
def submission_detail(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    reviewers = User.query.filter_by(role="reviewer").all()
    return render_template("admin/submission_detail.html", submission=sub, reviewers=reviewers)


@admin_bp.route("/submissions/<int:submission_id>/decide", methods=["POST"])
@login_required
@admin_required
def decide_submission(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    decision = request.form.get("decision")
    admin_notes = request.form.get("admin_notes", "")
    valid = ["accepted", "accepted_oral", "accepted_poster", "changes_requested", "rejected"]
    if decision in valid:
        sub.status = decision
        sub.admin_notes = admin_notes
        db.session.commit()
        flash(f"Submission status updated to '{sub.status_label}'.", "success")
    else:
        flash("Invalid decision.", "danger")
    return redirect(url_for("admin.submission_detail", submission_id=submission_id))


@admin_bp.route("/submissions/<int:submission_id>/assign-reviewer", methods=["POST"])
@login_required
@admin_required
def assign_reviewer(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    reviewer_id = parse_int(request.form.get("reviewer_id"), minimum=1)
    if reviewer_id is not None:
        existing = ReviewerAssignment.query.filter_by(
            reviewer_id=reviewer_id, submission_id=submission_id
        ).first()
        if not existing:
            reviewer = User.query.filter_by(id=reviewer_id, role="reviewer").first()
            if not reviewer:
                flash("Selected reviewer is invalid.", "danger")
                return redirect(url_for("admin.submission_detail", submission_id=submission_id))
            assignment = ReviewerAssignment(
                reviewer_id=reviewer_id,
                submission_id=submission_id,
                assigned_theme=sub.track.name if sub.track else "",
            )
            db.session.add(assignment)
            if sub.status in ("submitted", "resubmitted"):
                sub.status = "under_review"
            db.session.commit()
            flash("Reviewer assigned successfully.", "success")
        else:
            flash("Reviewer already assigned.", "info")
    else:
        flash("Please select a reviewer.", "warning")
    return redirect(url_for("admin.submission_detail", submission_id=submission_id))


@admin_bp.route("/reviews")
@login_required
@admin_required
def reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("admin/reviews.html", reviews=reviews)


@admin_bp.route("/agenda")
@login_required
@admin_required
def agenda():
    sessions = ScheduledSession.query.join(Submission).order_by(
        ScheduledSession.session_date, ScheduledSession.start_time
    ).all()
    accepted = Submission.query.filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster"])
    ).filter(~Submission.id.in_(
        db.session.query(ScheduledSession.submission_id)
    )).all()
    venues = Venue.query.all()
    return render_template("admin/agenda.html", sessions=sessions, accepted=accepted, venues=venues)


@admin_bp.route("/agenda/schedule", methods=["POST"])
@login_required
@admin_required
def schedule_submission():
    submission_id = parse_int(request.form.get("submission_id"), minimum=1)
    venue_id = parse_int(request.form.get("venue_id"), minimum=1)
    session_date = request.form.get("session_date")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    session_chair = request.form.get("session_chair", "")
    poster_board = request.form.get("poster_board", "")

    if submission_id is None or not session_date or not start_time or not end_time:
        flash("Submission, date, start time, and end time are required.", "danger")
        return redirect(url_for("admin.agenda"))

    sub = Submission.query.get_or_404(submission_id)
    if sub.scheduled_session:
        session = sub.scheduled_session
    else:
        session = ScheduledSession(submission_id=sub.id)
        db.session.add(session)

    session.venue_id = venue_id
    session.session_date = session_date
    session.start_time = start_time
    session.end_time = end_time
    session.session_chair = session_chair
    session.poster_board = poster_board or None
    sub.status = "scheduled"
    db.session.commit()
    flash("Presentation scheduled successfully.", "success")
    return redirect(url_for("admin.agenda"))


@admin_bp.route("/judging")
@login_required
@admin_required
def judging():
    submissions = Submission.query.filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).all()
    judges = User.query.filter_by(role="judge").all()
    return render_template("admin/judging.html", submissions=submissions, judges=judges)


@admin_bp.route("/results")
@login_required
@admin_required
def results():
    submissions = Submission.query.filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).all()
    ranked = []
    for sub in submissions:
        scores = [s for s in sub.judging_scores if s.status == "submitted"]
        if scores:
            avg = sum(s.total_score for s in scores if s.total_score) / len(scores)
            ranked.append((sub, round(avg, 1), scores))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return render_template("admin/results.html", ranked=ranked)


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    role_filter = request.args.get("role", "")
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    users = query.order_by(User.last_name).all()
    return render_template("admin/users.html", users=users, role_filter=role_filter)


@admin_bp.route("/venues", methods=["GET", "POST"])
@login_required
@admin_required
def venues():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        capacity = parse_int(request.form.get("capacity", 0), default=0, minimum=0)
        if not name:
            flash("Venue name is required.", "danger")
            return redirect(url_for("admin.venues"))
        venue = Venue(name=name, location=location, capacity=capacity)
        db.session.add(venue)
        db.session.commit()
        flash("Venue added.", "success")
        return redirect(url_for("admin.venues"))
    venues = Venue.query.all()
    return render_template("admin/venues.html", venues=venues)


@admin_bp.route("/assign-usher", methods=["POST"])
@login_required
@admin_required
def assign_usher():
    usher_id = parse_int(request.form.get("usher_id"), minimum=1)
    session_id = parse_int(request.form.get("session_id"), minimum=1)
    if usher_id is not None and session_id is not None:
        existing = UsherAssignment.query.filter_by(
            usher_id=usher_id, session_id=session_id
        ).first()
        if not existing:
            usher = User.query.filter_by(id=usher_id, role="usher").first()
            if not usher:
                flash("Selected usher is invalid.", "danger")
                return redirect(url_for("admin.agenda"))
            assignment = UsherAssignment(usher_id=usher_id, session_id=session_id)
            db.session.add(assignment)
            db.session.commit()
            flash("Usher assigned to session.", "success")
    else:
        flash("Please select both an usher and a session.", "warning")
    return redirect(url_for("admin.agenda"))
