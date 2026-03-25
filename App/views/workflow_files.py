import os

from flask import Response, current_app, jsonify, send_from_directory
from flask_jwt_extended import current_user

from App.controllers import role_required
from App.models import ReviewAssignment, Role, Submission, SubmissionVersion, SupplementaryMaterial

from .workflow_blueprint import workflow_views


@workflow_views.route("/workflow/uploads/supplementary/<path:file_name>", methods=["GET"])
@role_required(Role.Admin, Role.Author, Role.Reviewer)
def download_supplementary_file(file_name):
    material = SupplementaryMaterial.query.filter_by(file_name=file_name).first_or_404()
    submission = Submission.query.join(Submission.versions).filter(
        SubmissionVersion.id == material.submission_version_id
    ).first_or_404()

    is_author_owner = current_user.role.value == Role.Author.value and submission.creator_id == current_user.id
    is_reviewer_assigned = (
        current_user.role.value == Role.Reviewer.value
        and ReviewAssignment.query.filter_by(submission_id=submission.id, reviewer_id=current_user.id).first() is not None
    )
    is_admin = current_user.role.value == Role.Admin.value
    if not (is_author_owner or is_reviewer_assigned or is_admin):
        return jsonify({"message": "You do not have access to this file."}), 403

    upload_dir = os.path.abspath(os.path.join(current_app.config["UPLOADED_PHOTOS_DEST"], "supplementary"))
    return send_from_directory(upload_dir, file_name, as_attachment=True)
