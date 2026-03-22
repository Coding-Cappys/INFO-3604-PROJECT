from App.database import db
from App.models import Feedback, RSVP


def toggle_rsvp(user, session):
    existing = RSVP.query.filter_by(user_id=user.id, session_id=session.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return False

    rsvp = RSVP(user=user, session=session, status="Interested")
    db.session.add(rsvp)
    db.session.commit()
    return True


def submit_feedback(user, session, rating, comments):
    feedback = Feedback.query.filter_by(user_id=user.id, session_id=session.id).first()
    if feedback is None:
        feedback = Feedback(user=user, session=session)
        db.session.add(feedback)

    feedback.rating = int(rating) if rating else None
    feedback.comments = comments.strip() if comments else None
    db.session.commit()
    return feedback
