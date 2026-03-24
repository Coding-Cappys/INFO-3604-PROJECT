from App.database import db
from App.models import (
    Award,
    Digest,
    JudgeAssignment,
    Presentation,
    PresentationStatus,
    PresentationType,
    Session,
    SubmissionStatus,
    User,
)

from .workflow_common import WorkflowError, session_capacity_minutes


def record_editor_decision(submission, status):
    if status not in {
        SubmissionStatus.ChangesRequested,
        SubmissionStatus.AcceptedOral,
        SubmissionStatus.AcceptedPoster,
        SubmissionStatus.Rejected,
    }:
        raise WorkflowError("Unsupported editorial decision.")

    submission.status = status
    if status == SubmissionStatus.AcceptedOral:
        ensure_presentation(submission, PresentationType.Oral)
    elif status == SubmissionStatus.AcceptedPoster:
        ensure_presentation(submission, PresentationType.Poster)
    elif status in {SubmissionStatus.ChangesRequested, SubmissionStatus.Rejected} and submission.presentation:
        db.session.delete(submission.presentation)

    db.session.commit()
    return submission


def create_session(title, date_value, time_slot, venue, track_id=None, chair_id=None, usher_ids=None):
    usher_ids = usher_ids or []
    session = Session(
        title=title.strip(),
        date=date_value,
        time_slot=time_slot.strip() if time_slot else None,
        venue=venue.strip() if venue else None,
        track_id=track_id or None,
        chair_id=chair_id or None,
    )
    if usher_ids:
        session.ushers = User.query.filter(User.id.in_(usher_ids)).all()
    db.session.add(session)
    db.session.commit()
    return session


def assign_presentation_to_session(presentation, session, poster_location=None, duration_minutes=None):
    if duration_minutes is not None and duration_minutes <= 0:
        raise WorkflowError("Presentation duration must be a positive number of minutes.")

    if presentation.type == PresentationType.Poster and poster_location:
        existing_poster = Presentation.query.filter_by(
            session_id=session.id,
            poster_location=poster_location.strip(),
        ).filter(Presentation.id != presentation.id).first()
        if existing_poster is not None:
            raise WorkflowError("That poster location is already assigned in this session.")

    if presentation.type == PresentationType.Oral and duration_minutes is not None:
        capacity = session_capacity_minutes(session.time_slot)
        if capacity is not None:
            current_minutes = 0
            for existing in session.presentations:
                if existing.id == presentation.id or existing.type != PresentationType.Oral:
                    continue
                current_minutes += existing.duration_minutes or 0
            if current_minutes + duration_minutes > capacity:
                raise WorkflowError("This oral presentation exceeds the selected session time slot.")

    presentation.session = session
    presentation.poster_location = poster_location.strip() if poster_location else None
    presentation.duration_minutes = duration_minutes or presentation.duration_minutes
    presentation.status = PresentationStatus.Scheduled
    presentation.submission.status = SubmissionStatus.Scheduled
    db.session.commit()
    return presentation


def assign_judge(presentation, judge):
    existing = JudgeAssignment.query.filter_by(
        presentation_id=presentation.id,
        judge_id=judge.id,
    ).first()
    if existing:
        return existing

    assignment = JudgeAssignment(presentation=presentation, judge=judge)
    db.session.add(assignment)
    db.session.commit()
    return assignment


def assign_award_to_presentation(presentation, award_name, category=None):
    award_name = award_name.strip()
    if not award_name:
        raise WorkflowError("Award name is required.")

    award = Award.query.filter_by(name=award_name, category=category.strip() if category else None).first()
    if award is None:
        award = Award(name=award_name, category=category.strip() if category else None)
        db.session.add(award)
        db.session.flush()

    presentation.award = award
    presentation.status = PresentationStatus.AwardWinner
    db.session.commit()
    return award


def upsert_digest(year, summary, presentation_ids=None):
    summary = summary.strip()
    presentation_ids = presentation_ids or []

    if not summary:
        raise WorkflowError("Digest summary is required.")

    digests = Digest.query.filter_by(year=year).all()
    existing_by_presentation = {digest.presentation_id: digest for digest in digests}

    if not presentation_ids:
        presentation_ids = [None]

    kept = []
    for presentation_id in presentation_ids:
        digest = existing_by_presentation.get(presentation_id)
        if digest is None:
            digest = Digest(year=year, presentation_id=presentation_id)
            db.session.add(digest)
        digest.summary = summary
        kept.append(digest)

    for digest in digests:
        if digest not in kept:
            db.session.delete(digest)

    db.session.commit()
    return kept


def ensure_presentation(submission, presentation_type):
    presentation = submission.presentation
    if presentation is None:
        presentation = Presentation(submission=submission, type=presentation_type, status=PresentationStatus.Approved)
        db.session.add(presentation)
    else:
        presentation.type = presentation_type
        presentation.status = PresentationStatus.Approved
    return presentation
