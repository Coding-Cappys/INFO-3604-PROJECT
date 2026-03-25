from flask import flash, redirect, request, url_for

from App.controllers import WorkflowError, owner_or_role_required, role_required, submit_review
from App.models import ReviewAssignment, ReviewDecision, Role

from .workflow_blueprint import workflow_views


@workflow_views.route("/workflow/reviewer/assignments/<int:assignment_id>/review", methods=["POST"])
@role_required(Role.Reviewer)
def submit_review_action(assignment_id):
    assignment = ReviewAssignment.query.get_or_404(assignment_id)
    owner_or_role_required(assignment.reviewer_id, Role.Admin)
    decision = ReviewDecision(request.form["decision"])
    try:
        submit_review(assignment, decision, request.form.get("comments", ""))
        flash("Review submitted.")
    except WorkflowError as exc:
        flash(str(exc))
    return redirect(url_for("role_views.reviewer_assigned_abstracts"))
