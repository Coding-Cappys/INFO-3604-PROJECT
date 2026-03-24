from flask import flash, redirect, request, url_for

from App.controllers import owner_or_role_required, role_required, submit_score
from App.models import JudgeAssignment, Role

from .workflow_blueprint import workflow_views


@workflow_views.route("/workflow/judge/assignments/<int:assignment_id>/score", methods=["POST"])
@role_required(Role.Judge)
def submit_score_action(assignment_id):
    assignment = JudgeAssignment.query.get_or_404(assignment_id)
    owner_or_role_required(assignment.judge_id, Role.Admin)
    submit_score(assignment, request.form)
    flash("Score submitted.")
    return redirect(url_for("role_views.judge_assigned_presentations"))
