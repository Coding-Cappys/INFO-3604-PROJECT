import csv
import io
from datetime import datetime

from flask import Response, flash, jsonify, redirect, request, url_for

from App.controllers import (
    WorkflowError,
    assign_award_to_presentation,
    assign_judge,
    assign_presentation_to_session,
    assign_reviewer,
    create_session,
    record_editor_decision,
    role_required,
    upsert_digest,
)
from App.models import Attendance, Feedback, Presentation, Role, Session, Submission, SubmissionStatus, User

from .workflow_blueprint import workflow_views
from .workflow_helpers import int_list_from_form


@workflow_views.route("/workflow/admin/submissions/<int:submission_id>/assign-reviewer", methods=["POST"])
@role_required(Role.Admin)
def assign_reviewer_action(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    reviewer = User.query.get_or_404(request.form.get("reviewer_id", type=int))
    assign_reviewer(submission, reviewer)
    flash("Reviewer assigned.")
    return redirect(url_for("role_views.admin_review_management"))


@workflow_views.route("/workflow/admin/submissions/<int:submission_id>/decision", methods=["POST"])
@role_required(Role.Admin)
def record_decision_action(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    status = SubmissionStatus(request.form["status"])
    try:
        record_editor_decision(submission, status)
        flash("Editorial decision recorded.")
    except WorkflowError as exc:
        flash(str(exc))
    return redirect(url_for("role_views.admin_submissions"))


@workflow_views.route("/workflow/admin/sessions", methods=["POST"])
@role_required(Role.Admin)
def create_session_action():
    date_value = None
    raw_date = request.form.get("date")
    if raw_date:
        date_value = datetime.strptime(raw_date, "%Y-%m-%d").date()

    usher_ids = int_list_from_form("usher_ids")
    create_session(
        title=request.form["title"],
        date_value=date_value,
        time_slot=request.form.get("time_slot", ""),
        venue=request.form.get("venue", ""),
        track_id=request.form.get("track_id", type=int),
        chair_id=request.form.get("chair_id", type=int),
        usher_ids=usher_ids,
    )
    flash("Session created.")
    return redirect(url_for("role_views.admin_agenda_builder"))


@workflow_views.route("/workflow/admin/presentations/<int:presentation_id>/schedule", methods=["POST"])
@role_required(Role.Admin)
def schedule_presentation_action(presentation_id):
    presentation = Presentation.query.get_or_404(presentation_id)
    session = Session.query.get_or_404(request.form.get("session_id", type=int))
    try:
        assign_presentation_to_session(
            presentation,
            session,
            poster_location=request.form.get("poster_location", ""),
            duration_minutes=request.form.get("duration_minutes", type=int),
        )
        flash("Presentation scheduled.")
    except WorkflowError as exc:
        flash(str(exc))
    return redirect(url_for("role_views.admin_agenda_builder"))


@workflow_views.route("/workflow/admin/presentations/<int:presentation_id>/assign-judge", methods=["POST"])
@role_required(Role.Admin)
def assign_judge_action(presentation_id):
    presentation = Presentation.query.get_or_404(presentation_id)
    judge = User.query.get_or_404(request.form.get("judge_id", type=int))
    assign_judge(presentation, judge)
    flash("Judge assigned.")
    return redirect(url_for("role_views.admin_judging_results"))


@workflow_views.route("/workflow/admin/presentations/<int:presentation_id>/award", methods=["POST"])
@role_required(Role.Admin)
def assign_award_action(presentation_id):
    presentation = Presentation.query.get_or_404(presentation_id)
    try:
        assign_award_to_presentation(
            presentation,
            request.form.get("award_name", ""),
            request.form.get("category", ""),
        )
        flash("Award assigned.")
    except WorkflowError as exc:
        flash(str(exc))
    return redirect(url_for("role_views.admin_judging_results"))


@workflow_views.route("/workflow/admin/digest", methods=["POST"])
@role_required(Role.Admin)
def upsert_digest_action():
    presentation_ids = int_list_from_form("presentation_ids")
    try:
        upsert_digest(
            request.form.get("year", type=int) or datetime.utcnow().year,
            request.form.get("summary", ""),
            presentation_ids=presentation_ids,
        )
        flash("Digest updated.")
    except WorkflowError as exc:
        flash(str(exc))
    return redirect(url_for("role_views.admin_settings"))


@workflow_views.route("/workflow/admin/reports/<string:report_type>.csv", methods=["GET"])
@role_required(Role.Admin)
def export_report_action(report_type):
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "submissions":
        writer.writerow(["submission_id", "title", "status", "creator", "track", "submitted_at"])
        for submission in Submission.query.order_by(Submission.id).all():
            writer.writerow(
                [
                    submission.id,
                    submission.title,
                    submission.status.value if submission.status else "",
                    submission.creator.username if submission.creator else "",
                    submission.primary_track.name if submission.primary_track else "",
                    submission.submitted_at.isoformat() if submission.submitted_at else "",
                ]
            )
    elif report_type == "attendance":
        writer.writerow(["attendance_id", "user", "session", "venue", "check_in_time"])
        for attendance in Attendance.query.order_by(Attendance.id).all():
            writer.writerow(
                [
                    attendance.id,
                    attendance.user.username if attendance.user else "",
                    attendance.session.title if attendance.session else "",
                    attendance.session.venue if attendance.session else "",
                    attendance.check_in_time.isoformat() if attendance.check_in_time else "",
                ]
            )
    elif report_type == "feedback":
        writer.writerow(["feedback_id", "user", "session", "rating", "comments"])
        for feedback in Feedback.query.order_by(Feedback.id).all():
            writer.writerow(
                [
                    feedback.id,
                    feedback.user.username if feedback.user else "",
                    feedback.session.title if feedback.session else "",
                    feedback.rating or "",
                    feedback.comments or "",
                ]
            )
    else:
        return jsonify({"message": "Unknown report type"}), 404

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={report_type}-report.csv"
    return response
