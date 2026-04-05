import io
import qrcode
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from functools import wraps
from .. import db
from ..models import ScheduledSession, RSVP, SessionFeedback, Submission
from .utils import parse_rating

attendee_bp = Blueprint("attendee", __name__)


def attendee_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("attendee", "admin"):
            flash("Attendee access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@attendee_bp.route("/")
@login_required
@attendee_required
def dashboard():
    rsvps = RSVP.query.filter_by(attendee_id=current_user.id).all()
    rsvp_session_ids = {r.session_id for r in rsvps}
    sessions = ScheduledSession.query.join(Submission).filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).order_by(ScheduledSession.session_date, ScheduledSession.start_time).all()
    upcoming = [s for s in sessions if s.id in rsvp_session_ids]
    return render_template("attendee/dashboard.html", rsvps=rsvps, upcoming=upcoming,
                           rsvp_session_ids=rsvp_session_ids)


@attendee_bp.route("/schedule")
@login_required
@attendee_required
def schedule():
    sessions = ScheduledSession.query.join(Submission).filter(
        Submission.status.in_(["accepted", "accepted_oral", "accepted_poster", "scheduled"])
    ).order_by(ScheduledSession.session_date, ScheduledSession.start_time).all()
    rsvps = {r.session_id for r in RSVP.query.filter_by(attendee_id=current_user.id).all()}
    return render_template("attendee/schedule.html", sessions=sessions, rsvp_session_ids=rsvps)


@attendee_bp.route("/rsvp/<int:session_id>", methods=["POST"])
@login_required
@attendee_required
def rsvp(session_id):
    session = ScheduledSession.query.get_or_404(session_id)
    existing = RSVP.query.filter_by(attendee_id=current_user.id, session_id=session_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("RSVP removed.", "info")
    else:
        rsvp = RSVP(attendee_id=current_user.id, session_id=session_id)
        db.session.add(rsvp)
        db.session.commit()
        flash("RSVP confirmed!", "success")
    return redirect(request.referrer or url_for("attendee.schedule"))


@attendee_bp.route("/qr-code")
@login_required
@attendee_required
def qr_code():
    return render_template("attendee/qr_code.html")


@attendee_bp.route("/qr-code/image")
@login_required
@attendee_required
def qr_code_image():
    data = f"UWI-FESTIVAL-{current_user.id}-{current_user.email}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="image/png")


@attendee_bp.route("/feedback/<int:session_id>", methods=["GET", "POST"])
@login_required
@attendee_required
def feedback(session_id):
    session = ScheduledSession.query.get_or_404(session_id)
    existing = SessionFeedback.query.filter_by(user_id=current_user.id, session_id=session_id).first()
    if request.method == "POST":
        if existing:
            fb = existing
        else:
            fb = SessionFeedback(session_id=session_id, user_id=current_user.id)
            db.session.add(fb)
        fb.content_quality = parse_rating(request.form.get("content_quality"))
        fb.presentation_effectiveness = parse_rating(request.form.get("presentation_effectiveness"))
        fb.relevance = parse_rating(request.form.get("relevance"))
        fb.comments = request.form.get("comments", "").strip()
        db.session.commit()
        flash("Feedback submitted. Thank you!", "success")
        return redirect(url_for("attendee.schedule"))
    return render_template("attendee/feedback.html", session=session, feedback=existing)


@attendee_bp.route("/my-schedule")
@login_required
@attendee_required
def my_schedule():
    rsvps = RSVP.query.filter_by(attendee_id=current_user.id).all()
    session_ids = [r.session_id for r in rsvps]
    sessions = ScheduledSession.query.filter(ScheduledSession.id.in_(session_ids)).order_by(
        ScheduledSession.session_date, ScheduledSession.start_time
    ).all()
    return render_template("attendee/my_schedule.html", sessions=sessions)
