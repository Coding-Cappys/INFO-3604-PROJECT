from App.database import db
from App.models import PresentationStatus, Score


def submit_score(assignment, payload):
    score = assignment.score or Score(judge_assignment=assignment)
    db.session.add(score)
    score.research_quality = int(payload["research_quality"])
    score.clarity = int(payload["clarity"])
    score.innovation = int(payload["innovation"])
    score.response_to_questions = int(payload["response_to_questions"])
    score.overall_impact = int(payload["overall_impact"])
    score.comments = payload.get("comments", "").strip() or None

    assignment.presentation.status = PresentationStatus.Scored
    db.session.commit()
    return score
