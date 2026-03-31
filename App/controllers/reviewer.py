from App.database import db
from App.models import Review, ReviewDecision, ReviewSubmission, SubmissionStatus

from .workflow_common import WorkflowError


def normalize_review_decision(decision):
    if isinstance(decision, ReviewDecision):
        return decision

    mapping = {
        "Approve": ReviewDecision.ApproveOral,
        "ApproveOral": ReviewDecision.ApproveOral,
        "ApprovePoster": ReviewDecision.ApprovePoster,
        "RecommendPoster": ReviewDecision.ApprovePoster,
        "RequestChanges": ReviewDecision.RequestChanges,
        "Reject": ReviewDecision.Reject,
        "Rejected": ReviewDecision.Reject,
    }
    normalized = mapping.get(str(decision))
    if normalized is None:
        raise WorkflowError("Unsupported review decision.")
    return normalized


def assign_reviewer(submission, reviewer):
    existing = ReviewSubmission.query.filter_by(
        submission_id=submission.id,
        reviewer_id=reviewer.id,
    ).first()
    if existing:
        return existing

    assignment = ReviewSubmission(
        submission=submission,
        reviewer=reviewer,
        status="Pending",
    )
    db.session.add(assignment)
    submission.status = SubmissionStatus.InReview
    db.session.commit()
    return assignment


def submit_review(assignment, decision, comments):
    if assignment.review is not None:
        raise WorkflowError("A review has already been submitted for this assignment.")

    review = Review(
        review_submission=assignment,
        decision=normalize_review_decision(decision),
        comments=comments.strip() if comments else None,
    )
    assignment.status = "Completed"
    db.session.add(review)
    db.session.commit()
    return review
