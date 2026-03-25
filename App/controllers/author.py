from App.database import db
from App.models import Submission, SubmissionStatus, SubmissionVersion

from .workflow_common import (
    WorkflowError,
    attach_supplementary_materials,
    latest_submission_version,
    replace_submission_authors,
)


def create_submission(
    creator,
    title,
    abstract,
    keywords="",
    primary_track_id=None,
    secondary_track_id=None,
    author_ids=None,
    revision_notes=None,
    supplementary_files=None,
):
    author_ids = author_ids or [creator.id]
    supplementary_files = supplementary_files or []

    submission = Submission(
        title=title.strip(),
        keywords=keywords.strip() if keywords else None,
        creator=creator,
        primary_track_id=primary_track_id or None,
        secondary_track_id=secondary_track_id or None,
        status=SubmissionStatus.Draft,
    )
    db.session.add(submission)
    db.session.flush()

    version = SubmissionVersion(
        submission=submission,
        version_number=1,
        abstract=abstract.strip(),
        revision_notes=revision_notes.strip() if revision_notes else None,
    )
    db.session.add(version)

    replace_submission_authors(submission, author_ids, creator.id)
    attach_supplementary_materials(version, supplementary_files)
    db.session.commit()
    return submission


def update_submission(
    submission,
    title,
    abstract,
    keywords="",
    primary_track_id=None,
    secondary_track_id=None,
    author_ids=None,
    revision_notes=None,
    supplementary_files=None,
):
    if submission.status not in {SubmissionStatus.Draft, SubmissionStatus.ChangesRequested, SubmissionStatus.Submitted}:
        raise WorkflowError("This submission can no longer be edited.")

    author_ids = author_ids or [submission.creator_id]
    supplementary_files = supplementary_files or []

    submission.title = title.strip()
    submission.keywords = keywords.strip() if keywords else None
    submission.primary_track_id = primary_track_id or None
    submission.secondary_track_id = secondary_track_id or None

    latest = latest_submission_version(submission)
    next_version_number = 1 if latest is None else latest.version_number + 1
    version = SubmissionVersion(
        submission=submission,
        version_number=next_version_number,
        abstract=abstract.strip(),
        revision_notes=revision_notes.strip() if revision_notes else None,
    )
    db.session.add(version)
    replace_submission_authors(submission, author_ids, submission.creator_id)
    attach_supplementary_materials(version, supplementary_files)
    db.session.commit()
    return submission


def submit_submission(submission):
    if submission.status not in {SubmissionStatus.Draft, SubmissionStatus.ChangesRequested, SubmissionStatus.Submitted}:
        raise WorkflowError("This submission cannot be submitted in its current state.")

    submission.status = SubmissionStatus.Submitted
    db.session.commit()
    return submission
