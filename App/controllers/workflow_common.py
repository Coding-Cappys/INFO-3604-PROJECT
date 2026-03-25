import os
import uuid
from datetime import datetime

from flask import current_app
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from App.database import db
from App.models import (
    Presentation,
    QRCode,
    Score,
    Submission,
    SubmissionAuthor,
    SubmissionVersion,
    SupplementaryMaterial,
)


class WorkflowError(ValueError):
    pass


def latest_submission_version(submission):
    return submission.versions.order_by(SubmissionVersion.version_number.desc()).first()


def store_supplementary_uploads(uploaded_files):
    stored_files = []
    if not uploaded_files:
        return stored_files

    upload_dir = os.path.join(current_app.config["UPLOADED_PHOTOS_DEST"], "supplementary")
    os.makedirs(upload_dir, exist_ok=True)

    for uploaded_file in uploaded_files:
        original_name = secure_filename(uploaded_file.filename or "")
        if not original_name:
            continue
        token = uuid.uuid4().hex[:10]
        stored_name = f"{token}_{original_name}"
        uploaded_file.save(os.path.join(upload_dir, stored_name))
        stored_files.append(stored_name)

    return stored_files


def get_or_create_qr_code(user):
    if user.qr_code:
        return user.qr_code

    qr_code = QRCode(user=user, code=f"UWI-{user.id}-{uuid.uuid4().hex[:10].upper()}")
    db.session.add(qr_code)
    db.session.commit()
    return qr_code


def get_submission_detail_query():
    return Submission.query.options(
        joinedload(Submission.creator),
        joinedload(Submission.primary_track),
        joinedload(Submission.secondary_track),
        joinedload(Submission.presentation).joinedload(Presentation.session),
    )


def average_score_expression():
    return (
        (Score.research_quality + Score.clarity + Score.innovation + Score.response_to_questions + Score.overall_impact)
        / 5.0
    )


def replace_submission_authors(submission, author_ids, corresponding_author_id):
    SubmissionAuthor.query.filter_by(submission_id=submission.id).delete()
    seen = set()
    for index, author_id in enumerate(author_ids, start=1):
        if not author_id or author_id in seen:
            continue
        seen.add(author_id)
        db.session.add(
            SubmissionAuthor(
                submission_id=submission.id,
                user_id=author_id,
                author_order=index,
                is_corresponding=author_id == corresponding_author_id,
            )
        )


def attach_supplementary_materials(version, supplementary_files):
    for file_name in supplementary_files:
        cleaned_name = file_name.strip()
        if not cleaned_name:
            continue
        extension = cleaned_name.rsplit(".", 1)[-1].lower() if "." in cleaned_name else None
        db.session.add(
            SupplementaryMaterial(
                submission_version=version,
                file_name=cleaned_name,
                file_type=extension,
            )
        )


def session_capacity_minutes(time_slot):
    if not time_slot or "-" not in time_slot:
        return None
    try:
        start_raw, end_raw = [part.strip() for part in time_slot.split("-", 1)]
        start = datetime.strptime(start_raw, "%H:%M")
        end = datetime.strptime(end_raw, "%H:%M")
    except ValueError:
        return None

    delta = int((end - start).total_seconds() / 60)
    return delta if delta > 0 else None
