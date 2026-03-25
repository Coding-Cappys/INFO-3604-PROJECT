from flask import flash, redirect, request, url_for
from flask_jwt_extended import current_user

from App.controllers import (
    WorkflowError,
    create_submission,
    owner_or_role_required,
    role_required,
    submit_submission,
    update_submission,
)
from App.models import Role, Submission

from .workflow_blueprint import workflow_views
from .workflow_helpers import combined_supplementary_files, int_list_from_form


@workflow_views.route("/workflow/author/submissions/save", methods=["POST"])
@role_required(Role.Author)
def save_submission_action():
    submission_id = request.form.get("submission_id", type=int)
    author_ids = int_list_from_form("author_ids")
    if current_user.id not in author_ids:
        author_ids.insert(0, current_user.id)

    try:
        if submission_id:
            submission = Submission.query.get_or_404(submission_id)
            owner_or_role_required(submission.creator_id, Role.Admin)
            update_submission(
                submission,
                title=request.form["title"],
                abstract=request.form["abstract"],
                keywords=request.form.get("keywords", ""),
                primary_track_id=request.form.get("primary_track_id", type=int),
                secondary_track_id=request.form.get("secondary_track_id", type=int),
                author_ids=author_ids,
                revision_notes=request.form.get("revision_notes", ""),
                supplementary_files=combined_supplementary_files(),
            )
            flash("Submission updated.")
        else:
            create_submission(
                current_user,
                title=request.form["title"],
                abstract=request.form["abstract"],
                keywords=request.form.get("keywords", ""),
                primary_track_id=request.form.get("primary_track_id", type=int),
                secondary_track_id=request.form.get("secondary_track_id", type=int),
                author_ids=author_ids,
                revision_notes=request.form.get("revision_notes", ""),
                supplementary_files=combined_supplementary_files(),
            )
            flash("Draft created.")
    except WorkflowError as exc:
        flash(str(exc))
    return redirect(url_for("role_views.author_my_submissions"))


@workflow_views.route("/workflow/author/submissions/<int:submission_id>/submit", methods=["POST"])
@role_required(Role.Author)
def submit_submission_action(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    owner_or_role_required(submission.creator_id, Role.Admin)
    try:
        submit_submission(submission)
        flash("Submission sent for review.")
    except WorkflowError as exc:
        flash(str(exc))
    return redirect(url_for("role_views.author_status_tracking"))
