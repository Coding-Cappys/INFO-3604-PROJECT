from flask import Blueprint, render_template
from flask_login import current_user
from ..models import Submission, ScheduledSession, JudgingScore, Track, Venue
from ..models import RSVP

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    accepted = Submission.query.filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).limit(6).all()
    sessions = ScheduledSession.query.join(Submission).filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).order_by(ScheduledSession.session_date, ScheduledSession.start_time).limit(10).all()
    tracks = Track.query.all()
    stats = {
        "total_submissions": Submission.query.count(),
        "accepted": Submission.query.filter(
            Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
        ).count(),
        "tracks": len(tracks),
    }
    return render_template("public/index.html", accepted=accepted, sessions=sessions, tracks=tracks, stats=stats)


@public_bp.route("/schedule")
def schedule():
    sessions = (
        ScheduledSession.query.join(Submission)
        .join(Venue, isouter=True)
        .filter(Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"]))
        .order_by(ScheduledSession.session_date, ScheduledSession.start_time)
        .all()
    )
    tracks = Track.query.all()
    rsvp_session_ids = set()
    if current_user.is_authenticated and current_user.role == "attendee":
        rsvp_session_ids = {
            r.session_id for r in RSVP.query.filter_by(attendee_id=current_user.id).all()
        }
    return render_template(
        "public/schedule.html",
        sessions=sessions,
        tracks=tracks,
        rsvp_session_ids=rsvp_session_ids,
    )


@public_bp.route("/presentations")
def presentations():
    submissions = Submission.query.filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).order_by(Submission.title).all()
    tracks = Track.query.all()
    return render_template("public/presentations.html", submissions=submissions, tracks=tracks)


@public_bp.route("/presentations/<int:submission_id>")
def presentation_detail(submission_id):
    sub = Submission.query.filter(
        Submission.id == submission_id,
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).first_or_404()
    return render_template("public/presentation_detail.html", submission=sub)


@public_bp.route("/awards")
def awards():
    scored_submissions = (
        Submission.query
        .join(JudgingScore, isouter=True)
        .filter(Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"]))
        .all()
    )
    ranked = []
    for sub in scored_submissions:
        scores = [s for s in sub.judging_scores if s.status == "submitted"]
        if scores:
            avg = sum(s.total_score for s in scores if s.total_score) / len(scores)
            ranked.append((sub, round(avg, 1)))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return render_template("public/awards.html", ranked=ranked)


@public_bp.route("/digest")
def digest():
    submissions = Submission.query.filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).order_by(Submission.track_id, Submission.title).all()
    tracks = Track.query.all()
    return render_template("public/digest.html", submissions=submissions, tracks=tracks)
