
from flask import Blueprint, abort, render_template, request
from flask_jwt_extended import current_user

from App.controllers import (
    average_score_expression,
    get_or_create_qr_code,
    latest_submission_version,
    role_required,
)
from App.database import db
from App.models import (
    Attendance,
    Digest,
    Feedback,
    JudgeAssignment,
    Presentation,
    PresentationStatus,
    ReviewSubmission,
    Role,
    RSVP,
    Score,
    Session,
    Submission,
    SubmissionStatus,
    SubmissionVersion,
    SupplementaryMaterial,
    Track,
    User,
)

role_views = Blueprint("role_views", __name__, template_folder="../templates")


def _render_role_page(template_name, title, role_label, page_title, **kwargs):
    context = {
        "title": title,
        "role_label": role_label,
        "page_title": page_title,
    }
    context.update(kwargs)
    return render_template(template_name, **context)


@role_views.route("/role/author/create-submission", methods=["GET"])
@role_required(Role.Author)
def author_create_submission():
    submission = None
    latest_version = None
    edit_id = request.args.get("edit")
    if edit_id:
        submission = Submission.query.filter_by(id=edit_id, creator_id=current_user.id).first_or_404()
        latest_version = latest_submission_version(submission)

    tracks = Track.query.order_by(Track.name).all()
    authors = User.query.filter(User.role == Role.Author.value).order_by(User.name, User.username).all()
    return _render_role_page(
        "author/author_create_submission.html",
        "Author - Create Submission",
        "Author",
        "Create Submission",
        submission=submission,
        latest_version=latest_version,
        tracks=tracks,
        authors=authors,
    )


@role_views.route("/role/author/my-submissions", methods=["GET"])
@role_required(Role.Author)
def author_my_submissions():
    submissions = (
        Submission.query.filter_by(creator_id=current_user.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    return _render_role_page(
        "author/author_my_submissions.html",
        "Author - My Submissions",
        "Author",
        "My Submissions",
        submissions=submissions,
        latest_submission_version=latest_submission_version,
    )


@role_views.route("/role/submissions/<int:submission_id>", methods=["GET"])
@role_required(Role.Author, Role.Reviewer, Role.Admin)
def submission_detail(submission_id):
    submission = Submission.query.filter_by(id=submission_id).first_or_404()

    is_author_owner = current_user.role.value == Role.Author.value and submission.creator_id == current_user.id
    is_reviewer_assigned = (
        current_user.role.value == Role.Reviewer.value
        and ReviewSubmission.query.filter_by(submission_id=submission.id, reviewer_id=current_user.id).first() is not None
    )
    is_admin = current_user.role.value == Role.Admin.value

    if not (is_author_owner or is_reviewer_assigned or is_admin):
        abort(403)

    versions = submission.versions.order_by(SubmissionVersion.version_number.desc()).all()
    supplementary_files = (
        SupplementaryMaterial.query.join(SupplementaryMaterial.submission_version)
        .filter(SubmissionVersion.submission_id == submission.id)
        .order_by(SupplementaryMaterial.upload_date.desc())
        .all()
    )

    return _render_role_page(
        "submission/submission_detail.html",
        "Submission Detail",
        current_user.role.value,
        "Submission Detail",
        submission=submission,
        versions=versions,
        supplementary_files=supplementary_files,
    )


@role_views.route("/role/author/status-tracking", methods=["GET"])
@role_required(Role.Author)
def author_status_tracking():
    submissions = (
        Submission.query.filter_by(creator_id=current_user.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    return _render_role_page(
        "author/author_status_tracking.html",
        "Author - Status Tracking",
        "Author",
        "Status Tracking",
        submissions=submissions,
    )


@role_views.route("/role/author/reviewer-feedback", methods=["GET"])
@role_required(Role.Author)
def author_reviewer_feedback():
    submissions = (
        Submission.query.filter_by(creator_id=current_user.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    return _render_role_page(
        "author/author_reviewer_feedback.html",
        "Author - Reviewer Feedback",
        "Author",
        "Reviewer Feedback",
        submissions=submissions,
    )


@role_views.route("/role/reviewer/assigned-abstracts", methods=["GET"])
@role_required(Role.Reviewer)
def reviewer_assigned_abstracts():
    assignments = (
        ReviewSubmission.query.filter_by(reviewer_id=current_user.id)
        .order_by(ReviewSubmission.assigned_at.desc())
        .all()
    )
    return _render_role_page(
        "reviewer/reviewer_assigned_abstracts.html",
        "Reviewer - Assigned Abstracts",
        "Reviewer",
        "Assigned Abstracts",
        assignments=assignments,
        latest_submission_version=latest_submission_version,
    )


@role_views.route("/role/reviewer/my-reviews", methods=["GET"])
@role_required(Role.Reviewer)
def reviewer_my_reviews():
    assignments = (
        ReviewSubmission.query.filter_by(reviewer_id=current_user.id)
        .filter(ReviewSubmission.review.isnot(None))
        .order_by(ReviewSubmission.assigned_at.desc())
        .all()
    )
    return _render_role_page(
        "reviewer/reviewer_my_reviews.html",
        "Reviewer - My Reviews",
        "Reviewer",
        "My Reviews",
        assignments=assignments,
    )


@role_views.route("/role/reviewer/abstract-digest", methods=["GET"])
@role_required(Role.Reviewer)
def reviewer_abstract_digest():
    # SubmissionStatus in the current model doesn't include a "Draft" state.
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).all()
    return _render_role_page(
        "reviewer/reviewer_abstract_digest.html",
        "Reviewer - Abstract Digest",
        "Reviewer",
        "Abstract Digest",
        submissions=submissions,
        latest_submission_version=latest_submission_version,
    )


@role_views.route("/role/reviewer/guidelines", methods=["GET"])
@role_required(Role.Reviewer)
def reviewer_guidelines():
    assignments = ReviewSubmission.query.filter_by(reviewer_id=current_user.id).all()
    total = len(assignments)
    completed = sum(1 for assignment in assignments if assignment.review is not None)
    pending = total - completed
    avg_comment_length = 0
    completed_reviews = [assignment.review for assignment in assignments if assignment.review is not None]
    if completed_reviews:
        avg_comment_length = round(
            sum(len(review.comments or "") for review in completed_reviews) / len(completed_reviews)
        )
    metrics = {
        "assigned_reviews": total,
        "pending_reviews": pending,
        "completed_reviews": completed,
        "completion_rate": round((completed / total) * 100, 1) if total else 0,
        "avg_comment_length": avg_comment_length,
    }
    return _render_role_page(
        "reviewer/reviewer_guidelines.html",
        "Reviewer - Guidelines",
        "Reviewer",
        "Guidelines",
        metrics=metrics,
    )


@role_views.route("/role/reviewer/statistics", methods=["GET"])
@role_required(Role.Reviewer)
def reviewer_statistics():
    assignments = ReviewSubmission.query.filter_by(reviewer_id=current_user.id).all()
    total = len(assignments)
    completed = [assignment for assignment in assignments if assignment.review is not None]
    pending = total - len(completed)
    decision_breakdown = {
        "Approve": sum(1 for assignment in completed if assignment.review.decision.value == "Approve"),
        "RequestChanges": sum(1 for assignment in completed if assignment.review.decision.value == "RequestChanges"),
        "RecommendPoster": sum(1 for assignment in completed if assignment.review.decision.value == "RecommendPoster"),
    }
    theme_breakdown = []
    tracks = Track.query.order_by(Track.name).all()
    for track in tracks:
        track_assignments = [
            assignment for assignment in assignments if assignment.submission and assignment.submission.primary_track_id == track.id
        ]
        if not track_assignments:
            continue
        theme_breakdown.append(
            {
                "label": track.name,
                "total": len(track_assignments),
                "reviewed": sum(1 for assignment in track_assignments if assignment.review is not None),
                "pending": sum(1 for assignment in track_assignments if assignment.review is None),
            }
        )

    avg_comment_length = round(
        sum(len(assignment.review.comments or "") for assignment in completed) / len(completed)
    ) if completed else 0
    return _render_role_page(
        'reviewer/reviewer_statistics.html',
        'Reviewer - Statistics',
        'Reviewer',
        'Statistics',
    )


# Editor
@role_views.route('/role/editor/view-submissions', methods=['GET'])
def editor_view_submissions():
    from flask import request

    # Pagination
    PER_PAGE = 20
    page = request.args.get('page', 1, type=int)

    # Track filter (optional query param)
    track_id = request.args.get('track', None)

    # Query submissions, optionally filtered by track
    query = Submission.query.order_by(Submission.submitted_at.desc())
    if track_id:
        query = query.filter(Submission.track_id == track_id)

    total = query.count()
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, total_pages))
    submissions_raw = query.offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()

    # Normalise submission objects into simple dicts the template expects
    STATUS_MAP = {
        'Draft':         'unassigned',
        'Submitted':     'pending',
        'UnderReview':   'pending',
        'AcceptedOral':  'approved-oral',
        'AcceptedPoster':'approved-poster',
        'ChangesNeeded': 'revision',
        'Rejected':      'rejected',
    }

    submissions = []
    for s in submissions_raw:
        # Resolve reviewer ID from first active assignment, if any
        rid = None
        if hasattr(s, 'review_submissions'):
            try:
                first = s.review_submissions.first()
            except Exception:
                first = None
            if first is not None:
                if hasattr(first, 'reviewer') and first.reviewer:
                    rid = first.reviewer.id
                elif hasattr(first, 'reviewer_id'):
                    rid = first.reviewer_id

        submissions.append({
            'id':         s.id,
            'rid':        rid,
            'title':      s.title,
            'researcher': s.author.username if hasattr(s, 'author') and s.author else '—',
            'status':     STATUS_MAP.get(getattr(s, 'status', ''), 'unassigned'),
            'track':      getattr(s, 'track_id', ''),
        })

    # Build track list for the filter dropdown
    from App.models import Track
    try:
        tracks = Track.query.order_by(Track.name).all()
    except Exception:
        tracks = []

    return _render_role_page(
        'editor/editor_view_submissions.html',
        'Editor - View Track Submissions',
        'Editor',
        'View Submissions',
        submissions=submissions,
        tracks=tracks,
        page=page,
        total_pages=total_pages,
    )


@role_views.route('/role/editor/my-reviews', methods=['GET'])
def editor_my_reviews():
    return _render_role_page(
        'editor/editor_my_reviews.html',
        'Editor - My Reviews',
        'Editor',
        'My Reviews',
    )


@role_views.route('/role/editor/abstract-digest', methods=['GET'])
def editor_abstract_digest():
    return _render_role_page(
        'editor/editor_abstract_digest.html',
        'Editor - Abstract Digest',
        'Editor',
        'Abstract Digest',
    )


@role_views.route('/role/editor/guidelines', methods=['GET'])
def editor_guidelines():
    return _render_role_page(
        'editor/editor_guidelines.html',
        'Editor - Guidelines',
        'Editor',
        'Guidelines',
    )


@role_views.route('/role/editor/statistics', methods=['GET'])
def editor_statistics():
    return _render_role_page(
        'editor/editor_statistics.html',
        'Editor - Statistics',
        'Editor',
        'Statistics',
    )

# Judge
@role_views.route('/role/judge/assigned-presentations', methods=['GET'])
def judge_assigned_presentations():
    assignments = (
        JudgeAssignment.query.filter_by(judge_id=current_user.id)
        .order_by(JudgeAssignment.assigned_at.desc())
        .all()
    )
    return _render_role_page(
        "judge/judge_assigned_presentations.html",
        "Judge - Assigned Presentations",
        "Judge",
        "Assigned Presentations",
        assignments=assignments,
    )


@role_views.route("/role/judge/oral-presentations", methods=["GET"])
@role_required(Role.Judge)
def judge_oral_presentations():
    assignments = (
        JudgeAssignment.query.join(JudgeAssignment.presentation)
        .filter(JudgeAssignment.judge_id == current_user.id, Presentation.type == "Oral")
        .all()
    )
    return _render_role_page(
        "judge/judge_oral_presentations.html",
        "Judge - Oral Presentations",
        "Judge",
        "Oral Presentations",
        assignments=assignments,
    )


@role_views.route("/role/judge/poster-sessions", methods=["GET"])
@role_required(Role.Judge)
def judge_poster_sessions():
    assignments = (
        JudgeAssignment.query.join(JudgeAssignment.presentation)
        .filter(JudgeAssignment.judge_id == current_user.id, Presentation.type == "Poster")
        .all()
    )
    return _render_role_page(
        "judge/judge_poster_sessions.html",
        "Judge - Poster Sessions",
        "Judge",
        "Poster Sessions",
        assignments=assignments,
    )


@role_views.route("/role/judge/my-scores", methods=["GET"])
@role_required(Role.Judge)
def judge_my_scores():
    assignments = JudgeAssignment.query.filter_by(judge_id=current_user.id).all()
    return _render_role_page(
        "judge/judge_my_scores.html",
        "Judge - My Scores",
        "Judge",
        "My Scores",
        assignments=assignments,
    )


@role_views.route("/role/judge/results", methods=["GET"])
@role_required(Role.Judge)
def judge_results():
    ranking = (
        db.session.query(
            Presentation.id,
            Submission.title,
            db.func.avg(average_score_expression()).label("average_score"),
        )
        .join(Presentation.submission)
        .join(Presentation.judge_assignments)
        .join(JudgeAssignment.score)
        .group_by(Presentation.id, Submission.title)
        .order_by(db.desc("average_score"))
        .all()
    )
    return _render_role_page(
        "judge/judge_results.html",
        "Judge - Results",
        "Judge",
        "Results",
        ranking=ranking,
    )


@role_views.route("/role/judge/forms", methods=["GET"])
@role_required(Role.Judge)
def judge_forms():
    return judge_assigned_presentations()


@role_views.route("/role/attendee/schedule-agenda", methods=["GET"])
@role_required(Role.Attendee)
def attendee_schedule_agenda():
    sessions = Session.query.order_by(Session.date, Session.time_slot).all()
    rsvp_session_ids = {
        rsvp.session_id for rsvp in RSVP.query.filter_by(user_id=current_user.id).all()
    }
    return _render_role_page(
        "attendee/attendee_schedule_agenda.html",
        "Attendee - Schedule & Agenda",
        "Attendee",
        "Schedule & Agenda",
        sessions=sessions,
        rsvp_session_ids=rsvp_session_ids,
    )


@role_views.route("/role/attendee/my-schedule", methods=["GET"])
@role_required(Role.Attendee)
def attendee_my_schedule():
    rsvps = (
        RSVP.query.filter_by(user_id=current_user.id)
        .order_by(RSVP.session_id.desc())
        .all()
    )
    return _render_role_page(
        "attendee/attendee_my_schedule.html",
        "Attendee - My Schedule",
        "Attendee",
        "My Schedule",
        rsvps=rsvps,
    )


@role_views.route("/role/attendee/event-digest", methods=["GET"])
@role_required(Role.Attendee)
def attendee_event_digest():
    presentations = (
        Presentation.query.filter(Presentation.status.in_([PresentationStatus.Scheduled.value, PresentationStatus.Scored.value]))
        .order_by(Presentation.id.desc())
        .all()
    )
    return _render_role_page(
        "attendee/attendee_event_digest.html",
        "Attendee - Event Digest",
        "Attendee",
        "Event Digest",
        presentations=presentations,
    )


@role_views.route("/role/attendee/my-qr-code", methods=["GET"])
@role_required(Role.Attendee)
def attendee_my_qr_code():
    qr_code = get_or_create_qr_code(current_user)
    return _render_role_page(
        "attendee/attendee_my_qr_code.html",
        "Attendee - My QR Code",
        "Attendee",
        "My QR Code",
        qr_code=qr_code,
    )


@role_views.route("/role/attendee/qa-feedback", methods=["GET"])
@role_required(Role.Attendee)
def attendee_qa_feedback():
    feedbacks = Feedback.query.filter_by(user_id=current_user.id).all()
    attended_session_ids = [attendance.session_id for attendance in Attendance.query.filter_by(user_id=current_user.id).all()]
    attended_sessions = Session.query.filter(Session.id.in_(attended_session_ids)).all() if attended_session_ids else []
    return _render_role_page(
        "attendee/attendee_qa_feedback.html",
        "Attendee - Q&A & Feedback",
        "Attendee",
        "Q&A & Feedback",
        attended_sessions=attended_sessions,
        feedbacks=feedbacks,
    )


@role_views.route("/role/admin/submissions", methods=["GET"])
@role_required(Role.Admin)
def admin_submissions():
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(30).all()
    reviewers = User.query.filter(User.role == Role.Reviewer.value).order_by(User.username).all()
    status_counts = {
        status.value: Submission.query.filter_by(status=status.value).count()
        for status in SubmissionStatus
    }
    return _render_role_page(
        "admin/admin_submissions.html",
        "Administrator - Submissions",
        "Administrator",
        "Submissions",
        submissions=submissions,
        reviewers=reviewers,
        status_counts=status_counts,
    )


@role_views.route("/role/admin/review-management", methods=["GET"])
@role_required(Role.Admin)
def admin_review_management():
    assignments = ReviewSubmission.query.order_by(ReviewSubmission.assigned_at.desc()).limit(30).all()
    submitted_submissions = Submission.query.filter(
        Submission.status.in_([SubmissionStatus.Submitted.value, SubmissionStatus.InReview.value])
    ).all()
    reviewers = User.query.filter(User.role == Role.Reviewer.value).order_by(User.username).all()
    total_assignments = ReviewSubmission.query.count()
    reviewed = ReviewSubmission.query.join(ReviewSubmission.review).count()
    pending = total_assignments - reviewed
    return _render_role_page(
        "admin/admin_review_management.html",
        "Administrator - Review Management",
        "Administrator",
        "Review Management",
        assignments=assignments,
        total_assignments=total_assignments,
        reviewed=reviewed,
        pending=pending,
        submitted_submissions=submitted_submissions,
        reviewers=reviewers,
    )


@role_views.route("/role/admin/agenda-builder", methods=["GET"])
@role_required(Role.Admin)
def admin_agenda_builder():
    sessions = Session.query.order_by(Session.date, Session.time_slot).all()
    approved_presentations = Presentation.query.filter(
        Presentation.status.in_([PresentationStatus.Approved.value, PresentationStatus.Scheduled.value])
    ).all()
    tracks = Track.query.order_by(Track.name).all()
    ushers = User.query.filter(User.role == Role.Usher.value).order_by(User.username).all()
    return _render_role_page(
        "admin/admin_agenda_builder.html",
        "Administrator - Agenda Builder",
        "Administrator",
        "Agenda Builder",
        sessions=sessions,
        approved_presentations=approved_presentations,
        tracks=tracks,
        ushers=ushers,
    )


@role_views.route("/role/admin/judging-results", methods=["GET"])
@role_required(Role.Admin)
def admin_judging_results():
    judge_assignments = JudgeAssignment.query.order_by(JudgeAssignment.assigned_at.desc()).limit(30).all()
    judges = User.query.filter(User.role == Role.Judge.value).order_by(User.username).all()
    schedulable_presentations = Presentation.query.filter(
        Presentation.status.in_([PresentationStatus.Scheduled.value, PresentationStatus.Scored.value])
    ).all()
    total_scores = Score.query.count()
    avg_score = db.session.query(db.func.avg(average_score_expression())).scalar() or 0
    top_presentation_scores = (
        db.session.query(
            Presentation.id,
            Presentation.type,
            Submission.title,
            db.func.avg(average_score_expression()).label("average_score"),
        )
        .join(Presentation.submission)
        .join(Presentation.judge_assignments)
        .join(JudgeAssignment.score)
        .group_by(Presentation.id, Presentation.type, Submission.title)
        .order_by(db.desc("average_score"))
        .limit(10)
        .all()
    )
    awarded_presentations = Presentation.query.filter(Presentation.award_id.isnot(None)).all()
    return _render_role_page(
        "admin/admin_judging_results.html",
        "Administrator - Judging & Results",
        "Administrator",
        "Judging & Results",
        judge_assignments=judge_assignments,
        judges=judges,
        schedulable_presentations=schedulable_presentations,
        awarded_presentations=awarded_presentations,
        total_scores=total_scores,
        avg_score=round(avg_score, 2),
        top_presentation_scores=top_presentation_scores,
    )


@role_views.route("/role/admin/reports-analytics", methods=["GET"])
@role_required(Role.Admin)
def admin_reports_analytics():
    report = {
        "submissions": Submission.query.count(),
        "reviews": ReviewSubmission.query.count(),
        "presentations": Presentation.query.count(),
        "sessions": Session.query.count(),
        "attendance": Attendance.query.count(),
        "feedback": Feedback.query.count(),
    }
    submission_status_breakdown = [
        {"label": status.value, "count": Submission.query.filter_by(status=status.value).count()}
        for status in SubmissionStatus
    ]
    presentation_type_breakdown = [
        {"label": "Oral", "count": Presentation.query.filter_by(type="Oral").count()},
        {"label": "Poster", "count": Presentation.query.filter_by(type="Poster").count()},
    ]
    session_attendance = []
    for session in Session.query.order_by(Session.date, Session.time_slot).all():
        feedback_items = Feedback.query.filter_by(session_id=session.id).all()
        average_rating = 0
        if feedback_items:
            ratings = [item.rating for item in feedback_items if item.rating is not None]
            if ratings:
                average_rating = round(sum(ratings) / len(ratings), 2)
        session_attendance.append(
            {
                "session": session,
                "rsvp_count": RSVP.query.filter_by(session_id=session.id).count(),
                "attendance_count": Attendance.query.filter_by(session_id=session.id).count(),
                "feedback_count": len(feedback_items),
                "average_rating": average_rating,
            }
        )
    return _render_role_page(
        "admin/admin_reports_analytics.html",
        "Administrator - Reports & Analytics",
        "Administrator",
        "Reports & Analytics",
        report=report,
        submission_status_breakdown=submission_status_breakdown,
        presentation_type_breakdown=presentation_type_breakdown,
        session_attendance=session_attendance,
    )


@role_views.route("/role/admin/settings", methods=["GET"])
@role_required(Role.Admin)
def admin_settings():
    app_settings = {
        "conference_name": "UWI Research Awards & Festival",
        "conference_date": "2026-05-10 to 2026-05-13",
        "reviewers_per_submission": 2,
        "judging_criteria": [
            "Research Quality",
            "Clarity",
            "Innovation",
            "Response to Questions",
            "Overall Impact",
        ],
    }
    digests = Digest.query.order_by(Digest.year.desc(), Digest.id.asc()).all()
    publishable_presentations = Presentation.query.filter(Presentation.session_id.isnot(None)).all()
    return _render_role_page(
        "admin/admin_settings.html",
        "Administrator - Settings",
        "Administrator",
        "Settings",
        app_settings=app_settings,
        digests=digests,
        publishable_presentations=publishable_presentations,
    )


@role_views.route("/role/usher/my-sessions", methods=["GET"])
@role_required(Role.Usher)
def usher_my_sessions():
    sessions = current_user.ushered_sessions
    return _render_role_page(
        "usher/usher_my_sessions.html",
        "Usher - My Sessions",
        "Usher",
        "My Sessions",
        sessions=sessions,
    )


@role_views.route("/role/usher/check-in", methods=["GET"])
@role_required(Role.Usher)
def usher_check_in():
    sessions = current_user.ushered_sessions
    selected_session_id = request.args.get("session_id", type=int)
    selected_session = None
    if selected_session_id:
        selected_session = Session.query.filter_by(id=selected_session_id).first()
    if selected_session is None and sessions:
        selected_session = sessions[0]

    attendees = []
    checked_in_ids = set()
    if selected_session is not None:
        attendees = (
            User.query.join(RSVP, RSVP.user_id == User.id)
            .filter(RSVP.session_id == selected_session.id)
            .order_by(User.name, User.username)
            .all()
        )
        checked_in_ids = {
            attendance.user_id
            for attendance in Attendance.query.filter_by(session_id=selected_session.id).all()
        }

    return _render_role_page(
        "usher/usher_check_in.html",
        "Usher - Check-In",
        "Usher",
        "Check-In",
        sessions=sessions,
        selected_session=selected_session,
        attendees=attendees,
        checked_in_ids=checked_in_ids,
    )


@role_views.route("/role/usher/search-attendees", methods=["GET"])
@role_required(Role.Usher)
def usher_search_attendees():
    attendees = User.query.filter(User.role == Role.Attendee.value).order_by(User.username).all()
    return _render_role_page(
        "usher/usher_search_attendees.html",
        "Usher - Search Attendees",
        "Usher",
        "Search Attendees",
        attendees=attendees,
    )


@role_views.route("/role/usher/attendance-report", methods=["GET"])
@role_required(Role.Usher)
def usher_attendance_report():
    sessions = current_user.ushered_sessions
    report_rows = []
    for session in sessions:
        report_rows.append(
            {
                "session": session,
                "rsvp_count": RSVP.query.filter_by(session_id=session.id).count(),
                "attendance_count": Attendance.query.filter_by(session_id=session.id).count(),
            }
        )
    return _render_role_page(
        "usher/usher_attendance_report.html",
        "Usher - Attendance Report",
        "Usher",
        "Attendance Report",
        report_rows=report_rows,
    )
