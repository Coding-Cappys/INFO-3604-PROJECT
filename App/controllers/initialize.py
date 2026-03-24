from datetime import date

from App.database import db
from App.models import Role, SubmissionStatus, Track

from .user import create_user
from .workflow import (
    assign_award_to_presentation,
    assign_judge,
    assign_presentation_to_session,
    assign_reviewer,
    create_session,
    create_submission,
    record_editor_decision,
    submit_review,
    submit_submission,
    submit_score,
    toggle_rsvp,
    upsert_digest,
)


def initialize():
    db.drop_all()
    db.create_all()

    users = _seed_users()
    tracks = _seed_tracks()
    sessions = _seed_sessions(tracks, users)
    _seed_workflow_data(users, tracks, sessions)
    db.session.commit()


def _seed_users():
    users = {
        "admin": create_user(
            "admin",
            "adminpass",
            role=Role.Admin,
            name="Festival Administrator",
            email="admin@uwi.edu",
            affiliation="The UWI",
        ),
        "author": create_user(
            "alice",
            "alicepass",
            role=Role.Author,
            name="Alice Researcher",
            email="alice@uwi.edu",
            affiliation="The UWI",
            discipline="Education",
        ),
        "author_two": create_user(
            "ben",
            "benpass",
            role=Role.Author,
            name="Ben Scholar",
            email="ben@uwi.edu",
            affiliation="The UWI",
            discipline="Health",
        ),
        "reviewer": create_user(
            "rita",
            "ritapass",
            role=Role.Reviewer,
            name="Rita Reviewer",
            email="rita@uwi.edu",
            discipline="Education",
        ),
        "reviewer_two": create_user(
            "ron",
            "ronpass",
            role=Role.Reviewer,
            name="Ron Reviewer",
            email="ron@uwi.edu",
            discipline="Technology",
        ),
        "judge": create_user(
            "jane",
            "janepass",
            role=Role.Judge,
            name="Jane Judge",
            email="jane@uwi.edu",
        ),
        "attendee": create_user(
            "tom",
            "tompass",
            role=Role.Attendee,
            name="Tom Attendee",
            email="tom@uwi.edu",
        ),
        "usher": create_user(
            "uma",
            "umapass",
            role=Role.Usher,
            name="Uma Usher",
            email="uma@uwi.edu",
        ),
        "chair": create_user(
            "chris",
            "chrispass",
            role=Role.Admin,
            name="Chris Chair",
            email="chair@uwi.edu",
        ),
    }
    return users


def _seed_tracks():
    tracks = [
        Track(name="Education", theme="Innovative teaching and learning"),
        Track(name="Health", theme="Health and wellbeing"),
        Track(name="Technology", theme="Digital transformation"),
    ]
    db.session.add_all(tracks)
    db.session.commit()
    return tracks


def _seed_sessions(tracks, users):
    oral_session = create_session(
        "Education Oral Session",
        date(2026, 5, 10),
        "09:00 - 10:30",
        "FST Lecture Theatre",
        track_id=tracks[0].id,
        chair_id=users["chair"].id,
        usher_ids=[users["usher"].id],
    )
    poster_session = create_session(
        "Innovation Poster Session",
        date(2026, 5, 11),
        "13:00 - 14:30",
        "Student Union Hall",
        track_id=tracks[2].id,
        chair_id=users["chair"].id,
        usher_ids=[users["usher"].id],
    )
    return {"oral": oral_session, "poster": poster_session}


def _seed_workflow_data(users, tracks, sessions):
    accepted = create_submission(
        users["author"],
        "Adaptive Learning Pathways for Caribbean Classrooms",
        "This study explores adaptive learning pathways in blended classrooms across the Caribbean.",
        keywords="education, adaptive learning, caribbean",
        primary_track_id=tracks[0].id,
        author_ids=[users["author"].id, users["author_two"].id],
        supplementary_files=["adaptive-learning.pdf"],
    )
    submit_submission(accepted)
    review_assignment = assign_reviewer(accepted, users["reviewer"])
    submit_review(review_assignment, decision="Approve", comments="Strong educational contribution.")
    record_editor_decision(accepted, SubmissionStatus.AcceptedOral)
    assign_presentation_to_session(accepted.presentation, sessions["oral"], duration_minutes=15)
    judge_assignment = assign_judge(accepted.presentation, users["judge"])
    submit_score(
        judge_assignment,
        {
            "research_quality": 4,
            "clarity": 5,
            "innovation": 4,
            "response_to_questions": 4,
            "overall_impact": 5,
            "comments": "Clear and engaging presentation.",
        },
    )
    assign_award_to_presentation(accepted.presentation, "Best Oral Presentation", "Oral")

    revision = create_submission(
        users["author_two"],
        "Community Health Dashboards for Small Islands",
        "A dashboard-driven approach to monitoring health interventions in island communities.",
        keywords="health, dashboards",
        primary_track_id=tracks[1].id,
        author_ids=[users["author_two"].id],
        supplementary_files=["health-dashboards.docx"],
    )
    submit_submission(revision)
    review_assignment = assign_reviewer(revision, users["reviewer_two"])
    submit_review(review_assignment, decision="RequestChanges", comments="Clarify the sampling methodology.")
    record_editor_decision(revision, SubmissionStatus.ChangesRequested)

    poster = create_submission(
        users["author"],
        "AI-assisted Research Support for Campus Services",
        "A pilot on AI-assisted student research support services across campus units.",
        keywords="ai, research support",
        primary_track_id=tracks[2].id,
        author_ids=[users["author"].id],
        supplementary_files=["campus-support-slides.pptx"],
    )
    submit_submission(poster)
    review_assignment = assign_reviewer(poster, users["reviewer_two"])
    submit_review(review_assignment, decision="RecommendPoster", comments="Good fit for poster discussion.")
    record_editor_decision(poster, SubmissionStatus.AcceptedPoster)
    assign_presentation_to_session(
        poster.presentation,
        sessions["poster"],
        poster_location="B-12",
        duration_minutes=10,
    )
    assign_award_to_presentation(poster.presentation, "Best Poster Presentation", "Poster")

    toggle_rsvp(users["attendee"], sessions["oral"])
    upsert_digest(
        2026,
        "The 2026 festival highlights adaptive learning, community health, and AI-enabled research support across the UWI.",
        presentation_ids=[accepted.presentation.id, poster.presentation.id],
    )
