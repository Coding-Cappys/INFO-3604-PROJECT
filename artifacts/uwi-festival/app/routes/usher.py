from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from .. import db
from ..models import ScheduledSession, UsherAssignment, AttendanceRecord, User, Submission
from .utils import parse_int

usher_bp = Blueprint("usher", __name__)


def usher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("usher", "admin"):
            flash("Usher access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@usher_bp.route("/")
@login_required
@usher_required
def dashboard():
    sessions = ScheduledSession.query.join(Submission).order_by(
        ScheduledSession.session_date, ScheduledSession.start_time
    ).all()
    recent_checkins = AttendanceRecord.query.order_by(
        AttendanceRecord.checked_in_at.desc()
    ).limit(20).all()
    return render_template("usher/dashboard.html", sessions=sessions, recent_checkins=recent_checkins)


@usher_bp.route("/checkin", methods=["POST"])
@login_required
@usher_required
def checkin():
    session_id = request.form.get("session_id")
    attendee_query = request.form.get("attendee_query", "").strip()
    scanned_via_qr = request.form.get("scan_method") == "qr"

    if not session_id or not attendee_query:
        flash("Please select a session and enter an attendee ID or email.", "warning")
        return redirect(url_for("usher.dashboard"))

    parsed_session_id = parse_int(session_id, minimum=1)
    if parsed_session_id is None:
        flash("Invalid session selected.", "danger")
        return redirect(url_for("usher.dashboard"))

    session = ScheduledSession.query.get_or_404(parsed_session_id)

    attendee = None
    if attendee_query.isdigit():
        attendee = User.query.filter_by(id=int(attendee_query), role="attendee").first()
    if not attendee:
        attendee = User.query.filter(
            User.email.ilike(attendee_query),
            User.role == "attendee"
        ).first()
    if not attendee:
        attendee = User.query.filter(
            (User.first_name + " " + User.last_name).ilike(f"%{attendee_query}%"),
            User.role == "attendee"
        ).first()

    if not attendee:
        if scanned_via_qr:
            flash("QR scan was not successful. Please rescan or enter attendee ID/email manually.", "danger")
        else:
            flash(f"No attendee found matching '{attendee_query}'.", "danger")
        return redirect(url_for("usher.dashboard"))

    existing = AttendanceRecord.query.filter_by(
        session_id=session.id, attendee_id=attendee.id
    ).first()
    if existing:
        if scanned_via_qr:
            flash(f"QR scan successful. {attendee.full_name} is already checked in.", "info")
        else:
            flash(f"{attendee.full_name} is already checked in.", "info")
    else:
        record = AttendanceRecord(
            session_id=session.id,
            attendee_id=attendee.id,
            usher_id=current_user.id,
            method="manual",
        )
        db.session.add(record)
        db.session.commit()
        if scanned_via_qr:
            flash(f"QR scan successful. {attendee.full_name} checked in successfully!", "success")
        else:
            flash(f"{attendee.full_name} checked in successfully!", "success")

    return redirect(url_for("usher.dashboard"))


@usher_bp.route("/session/<int:session_id>")
@login_required
@usher_required
def session_checkin(session_id):
    session = ScheduledSession.query.get_or_404(session_id)
    attendance = AttendanceRecord.query.filter_by(session_id=session_id).all()
    checked_in_ids = {a.attendee_id for a in attendance}
    attendees = User.query.filter_by(role="attendee").all()
    return render_template("usher/checkin.html", session=session, attendance=attendance,
                           attendees=attendees, checked_in_ids=checked_in_ids)
