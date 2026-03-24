import io
import os

import pytest

from App.controllers import initialize
from App.main import create_app
from App.database import db
from App.models import Attendance, JudgeAssignment, Presentation, ReviewAssignment, RSVP, Session, Submission, SubmissionStatus, SupplementaryMaterial


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///workflow-test.db",
        }
    )
    with app.app_context():
        initialize()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    with app.test_client() as test_client:
        yield test_client


def login(client, username, password):
    response = client.post(
        "/api/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200


def test_author_admin_reviewer_judge_attendee_and_usher_flow(app, client):
    login(client, "alice", "alicepass")

    response = client.post(
        "/workflow/author/submissions/save",
        data={
            "title": "Workflow Integration Submission",
            "abstract": "This abstract validates the multi-role workflow.",
            "keywords": "workflow, testing",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Draft created" in response.data

    with app.app_context():
        submission = Submission.query.filter_by(title="Workflow Integration Submission").first()
        submission_id = submission.id

    response = client.post(
        f"/workflow/author/submissions/{submission_id}/submit",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Submission sent for review" in response.data

    client.get("/logout")
    login(client, "admin", "adminpass")
    response = client.post(
        f"/workflow/admin/submissions/{submission_id}/assign-reviewer",
        data={"reviewer_id": 5},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Reviewer assigned" in response.data

    with app.app_context():
        submission = Submission.query.get(submission_id)
        assert submission.status == SubmissionStatus.UnderReview
        assignment = ReviewAssignment.query.filter_by(submission_id=submission_id, reviewer_id=5).first()
        assignment_id = assignment.id

    client.get("/logout")
    login(client, "ron", "ronpass")
    response = client.post(
        f"/workflow/reviewer/assignments/{assignment_id}/review",
        data={"decision": "Approve", "comments": "Ready for an oral presentation."},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Review submitted" in response.data

    client.get("/logout")
    login(client, "admin", "adminpass")
    response = client.post(
        f"/workflow/admin/submissions/{submission_id}/decision",
        data={"status": "AcceptedOral"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Editorial decision recorded" in response.data

    with app.app_context():
        presentation = Presentation.query.filter_by(submission_id=submission_id).first()
        session = Session.query.filter_by(title="Education Oral Session").first()
        presentation_id = presentation.id
        session_id = session.id

    response = client.post(
        f"/workflow/admin/presentations/{presentation_id}/schedule",
        data={"session_id": session_id, "duration_minutes": 12},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Presentation scheduled" in response.data

    response = client.post(
        f"/workflow/admin/presentations/{presentation_id}/assign-judge",
        data={"judge_id": 6},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Judge assigned" in response.data

    with app.app_context():
        judge_assignment = JudgeAssignment.query.filter_by(presentation_id=presentation_id, judge_id=6).first()
        judge_assignment_id = judge_assignment.id

    client.get("/logout")
    login(client, "jane", "janepass")
    response = client.post(
        f"/workflow/judge/assignments/{judge_assignment_id}/score",
        data={
            "research_quality": 5,
            "clarity": 4,
            "innovation": 4,
            "response_to_questions": 4,
            "overall_impact": 5,
            "comments": "Strong presentation.",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Score submitted" in response.data

    client.get("/logout")
    login(client, "tom", "tompass")
    response = client.post(f"/workflow/attendee/sessions/{session_id}/rsvp")
    assert response.status_code == 200
    rsvp_payload = response.get_json()
    if not rsvp_payload["rsvp"]:
        response = client.post(f"/workflow/attendee/sessions/{session_id}/rsvp")
        rsvp_payload = response.get_json()
    assert rsvp_payload["rsvp"] is True

    client.get("/logout")
    login(client, "uma", "umapass")
    response = client.post(f"/workflow/usher/sessions/{session_id}/checkin/7")
    assert response.status_code == 200
    assert response.get_json()["checked_in"] is True

    with app.app_context():
        assert RSVP.query.filter_by(user_id=7, session_id=session_id).count() == 1
        assert Attendance.query.filter_by(user_id=7, session_id=session_id).count() == 1


def test_role_protection_blocks_non_admin_access(client):
    login(client, "tom", "tompass")
    response = client.get("/role/admin/submissions", follow_redirects=False)
    assert response.status_code in {302, 303, 403}


def test_public_pages_are_available_without_login(app):
    with app.test_client() as client:
        for path in ["/", "/schedule", "/presentations", "/digest", "/awards"]:
            response = client.get(path)
            assert response.status_code == 200


def test_public_presentation_detail_is_available(app):
    with app.app_context():
        presentation = Presentation.query.first()
        presentation_id = presentation.id

    with app.test_client() as client:
        response = client.get(f"/presentations/{presentation_id}")
        assert response.status_code == 200
        assert b"Presentation Details" in response.data or b"Abstract" in response.data


def test_author_can_upload_and_download_supplementary_files(app, client):
    login(client, "alice", "alicepass")
    response = client.post(
        "/workflow/author/submissions/save",
        data={
            "title": "Supplementary Upload Submission",
            "abstract": "Upload handling validation.",
            "keywords": "upload",
            "supplementary_uploads": (io.BytesIO(b"sample supplementary content"), "appendix.txt"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        submission = Submission.query.filter_by(title="Supplementary Upload Submission").first()
        material = (
            SupplementaryMaterial.query.join(SupplementaryMaterial.submission_version)
            .filter_by(submission_id=submission.id)
            .first()
        )
        assert material is not None
        file_path = os.path.join(app.config["UPLOADED_PHOTOS_DEST"], "supplementary", material.file_name)
        assert os.path.exists(file_path)

    detail_response = client.get(f"/role/submissions/{submission.id}")
    assert detail_response.status_code == 200
    assert b"Supplementary Files" in detail_response.data

    download_response = client.get(f"/workflow/uploads/supplementary/{material.file_name}")
    assert download_response.status_code == 200
    assert download_response.data == b"sample supplementary content"


def test_admin_can_export_reports_csv(app, client):
    login(client, "admin", "adminpass")
    response = client.get("/workflow/admin/reports/submissions.csv")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"submission_id,title,status" in response.data


def test_reviewer_statistics_page_uses_live_data(client):
    login(client, "rita", "ritapass")
    response = client.get("/role/reviewer/statistics")
    assert response.status_code == 200
    assert b"Review Statistics" in response.data
    assert b"Decision Breakdown" in response.data


def test_admin_schedule_validation_blocks_overbooked_session(app, client):
    login(client, "admin", "adminpass")
    with app.app_context():
        submission = Submission.query.filter_by(title="Community Health Dashboards for Small Islands").first()
        from App.controllers import record_editor_decision
        record_editor_decision(submission, SubmissionStatus.AcceptedOral)
        presentation = Presentation.query.filter_by(submission_id=submission.id).first()
        session = Session.query.filter_by(title="Education Oral Session").first()

    response = client.post(
        f"/workflow/admin/presentations/{presentation.id}/schedule",
        data={"session_id": session.id, "duration_minutes": 120},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"exceeds the selected session time slot" in response.data
