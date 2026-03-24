from flask import flash, jsonify, redirect, request, url_for
from flask_jwt_extended import current_user

from App.controllers import role_required, submit_feedback, toggle_rsvp
from App.models import Role, Session

from .workflow_blueprint import workflow_views


@workflow_views.route("/workflow/attendee/sessions/<int:session_id>/rsvp", methods=["POST"])
@role_required(Role.Attendee)
def toggle_rsvp_action(session_id):
    session = Session.query.get_or_404(session_id)
    is_rsvp = toggle_rsvp(current_user, session)
    if request.path.startswith("/workflow/attendee"):
        return jsonify({"rsvp": is_rsvp})
    flash("RSVP updated.")
    return redirect(url_for("role_views.attendee_schedule_agenda"))


@workflow_views.route("/workflow/attendee/sessions/<int:session_id>/feedback", methods=["POST"])
@role_required(Role.Attendee)
def submit_feedback_action(session_id):
    session = Session.query.get_or_404(session_id)
    submit_feedback(current_user, session, request.form.get("rating"), request.form.get("comments", ""))
    flash("Feedback saved.")
    return redirect(url_for("role_views.attendee_qa_feedback"))
