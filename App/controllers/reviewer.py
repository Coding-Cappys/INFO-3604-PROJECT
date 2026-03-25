from App.database import db
from App.models import Review, ReviewAssignment, SubmissionStatus

from .workflow_common import WorkflowError


def assign_reviewer(submission, reviewer):
    existing = ReviewAssignment.query.filter_by(
        submission_id=submission.id,
        reviewer_id=reviewer.id,
    ).first()
    if existing:
        return existing

    assignment = ReviewAssignment(
        submission=submission,
        reviewer=reviewer,
        status="Pending",
    )
    db.session.add(assignment)
    submission.status = SubmissionStatus.UnderReview
    db.session.commit()
    return assignment


def submit_review(assignment, decision, comments):
    if assignment.review is not None:
        raise WorkflowError("A review has already been submitted for this assignment.")

    review = Review(
        assignment=assignment,
        decision=decision,
        comments=comments.strip() if comments else None,
    )
    assignment.status = "Completed"
    db.session.add(review)
    db.session.commit()
    return review
