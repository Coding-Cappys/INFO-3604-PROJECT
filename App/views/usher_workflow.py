from flask import jsonify

from App.controllers import check_in_attendee, role_required
from App.models import Role, Session, User

from .workflow_blueprint import workflow_views


@workflow_views.route("/workflow/usher/sessions/<int:session_id>/checkin/<int:user_id>", methods=["POST"])
@role_required(Role.Usher)
def check_in_attendee_action(session_id, user_id):
    session = Session.query.get_or_404(session_id)
    attendee = User.query.get_or_404(user_id)
    attendance = check_in_attendee(attendee, session)
    return jsonify(
        {
            "checked_in": True,
            "attendance_id": attendance.id,
            "checked_in_time": attendance.check_in_time.isoformat(),
        }
    )
