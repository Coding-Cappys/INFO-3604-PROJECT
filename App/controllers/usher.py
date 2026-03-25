from datetime import datetime

from App.database import db
from App.models import Attendance


def check_in_attendee(user, session):
    attendance = Attendance.query.filter_by(user_id=user.id, session_id=session.id).first()
    if attendance:
        return attendance

    attendance = Attendance(user=user, session=session, check_in_time=datetime.utcnow())
    user.checked_in = True
    db.session.add(attendance)
    db.session.commit()
    return attendance
