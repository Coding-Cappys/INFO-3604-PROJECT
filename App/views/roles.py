from flask import Blueprint, render_template
from App.models import User, Role
from App.database import db
from flask import jsonify
from App.models import Attendance

from App.database import db
from App.models import (
    Submission,
    ReviewAssignment,
    Presentation,
    Session,
    JudgeAssignment,
    Score,
)

role_views = Blueprint('role_views', __name__, template_folder='../templates')


def _render_role_page(template_name, title, role_label, page_title, **kwargs):
    context = {
        'title': title,
        'role_label': role_label,
        'page_title': page_title,
    }
    context.update(kwargs)
    return render_template(template_name, **context)


# Author
@role_views.route('/role/author/create-submission', methods=['GET'])
def author_create_submission():
    return _render_role_page(
        'author/author_create_submission.html',
        'Author - Create Submission',
        'Author',
        'Create Submission',
    )


@role_views.route('/role/author/my-submissions', methods=['GET'])
def author_my_submissions():
    return _render_role_page(
        'author/author_my_submissions.html',
        'Author - My Submissions',
        'Author',
        'My Submissions',
    )


@role_views.route('/role/author/status-tracking', methods=['GET'])
def author_status_tracking():
    return _render_role_page(
        'author/author_status_tracking.html',
        'Author - Status Tracking',
        'Author',
        'Status Tracking',
    )


@role_views.route('/role/author/reviewer-feedback', methods=['GET'])
def author_reviewer_feedback():
    return _render_role_page(
        'author/author_reviewer_feedback.html',
        'Author - Reviewer Feedback',
        'Author',
        'Reviewer Feedback',
    )


# Reviewer
@role_views.route('/role/reviewer/assigned-abstracts', methods=['GET'])
def reviewer_assigned_abstracts():
    return _render_role_page(
        'reviewer/reviewer_assigned_abstracts.html',
        'Reviewer - Assigned Abstracts',
        'Reviewer',
        'Assigned Abstracts',
    )


@role_views.route('/role/reviewer/my-reviews', methods=['GET'])
def reviewer_my_reviews():
    return _render_role_page(
        'reviewer/reviewer_my_reviews.html',
        'Reviewer - My Reviews',
        'Reviewer',
        'My Reviews',
    )


@role_views.route('/role/reviewer/abstract-digest', methods=['GET'])
def reviewer_abstract_digest():
    return _render_role_page(
        'reviewer/reviewer_abstract_digest.html',
        'Reviewer - Abstract Digest',
        'Reviewer',
        'Abstract Digest',
    )


@role_views.route('/role/reviewer/guidelines', methods=['GET'])
def reviewer_guidelines():
    return _render_role_page(
        'reviewer/reviewer_guidelines.html',
        'Reviewer - Guidelines',
        'Reviewer',
        'Guidelines',
    )


@role_views.route('/role/reviewer/statistics', methods=['GET'])
def reviewer_statistics():
    return _render_role_page(
        'reviewer/reviewer_statistics.html',
        'Reviewer - Statistics',
        'Reviewer',
        'Statistics',
    )


# Judge
@role_views.route('/role/judge/assigned-presentations', methods=['GET'])
def judge_assigned_presentations():
    return _render_role_page(
        'judge/judge_assigned_presentations.html',
        'Judge - Assigned Presentations',
        'Judge',
        'Assigned Presentations',
    )


@role_views.route('/role/judge/oral-presentations', methods=['GET'])
def judge_oral_presentations():
    return _render_role_page(
        'judge/judge_oral_presentations.html',
        'Judge - Oral Presentations',
        'Judge',
        'Oral Presentations',
    )


@role_views.route('/role/judge/poster-sessions', methods=['GET'])
def judge_poster_sessions():
    return _render_role_page(
        'judge/judge_poster_sessions.html',
        'Judge - Poster Sessions',
        'Judge',
        'Poster Sessions',
    )


@role_views.route('/role/judge/my-scores', methods=['GET'])
def judge_my_scores():
    return _render_role_page(
        'judge/judge_my_scores.html',
        'Judge - My Scores',
        'Judge',
        'My Scores',
    )


@role_views.route('/role/judge/results', methods=['GET'])
def judge_results():
    return _render_role_page(
        'judge/judge_results.html',
        'Judge - Results',
        'Judge',
        'Results',
    )

@role_views.route('/role/judge/forms', methods=['GET'])
def judge_forms():
    submission = {
        "id": '1',
        "presenter": "Prof. Venkatesan Sundaram",
        "title": "Sustainable Futures: Building Resilient Communities",
        "theme": "Education, Culture, Sports, Equality, Law and Governance"
    }
    
    return _render_role_page(
        'judge/judge_forms.html',
        'Judge - Forms',
        'Judge',
        'Forms',
    )

# Attendee
@role_views.route('/role/attendee/schedule-agenda', methods=['GET'])
def attendee_schedule_agenda():
    return _render_role_page(
        'attendee/attendee_schedule_agenda.html',
        'Attendee - Schedule & Agenda',
        'Attendee',
        'Schedule & Agenda',
    )


@role_views.route('/role/attendee/my-schedule', methods=['GET'])
def attendee_my_schedule():
    return _render_role_page(
        'attendee/attendee_my_schedule.html',
        'Attendee - My Schedule',
        'Attendee',
        'My Schedule',
    )


@role_views.route('/role/attendee/presentations', methods=['GET'])
def attendee_presentations():
    return _render_role_page(
        'attendee/attendee_presentations.html',
        'Attendee - Presentations',
        'Attendee',
        'Presentations',
    )


@role_views.route('/role/attendee/my-qr-code', methods=['GET'])
def attendee_my_qr_code():
    return _render_role_page(
        'attendee/attendee_my_qr_code.html',
        'Attendee - My QR Code',
        'Attendee',
        'My QR Code',
    )


@role_views.route('/role/attendee/qa-feedback', methods=['GET'])
def attendee_qa_feedback():
    return _render_role_page(
        'attendee/attendee_qa_feedback.html',
        'Attendee - Q&A & Feedback',
        'Attendee',
        'Q&A & Feedback',
    )


# Admin
@role_views.route('/role/admin/submissions', methods=['GET'])
def admin_submissions():
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(20).all()
    status_counts = {
        'Draft': Submission.query.filter_by(status='Draft').count(),
        'Submitted': Submission.query.filter_by(status='Submitted').count(),
        'UnderReview': Submission.query.filter_by(status='UnderReview').count(),
        'AcceptedOral': Submission.query.filter_by(status='AcceptedOral').count(),
        'AcceptedPoster': Submission.query.filter_by(status='AcceptedPoster').count(),
        'Rejected': Submission.query.filter_by(status='Rejected').count(),
    }
    return _render_role_page(
        'admin/admin_submissions.html',
        'Administrator - Submissions',
        'Administrator',
        'Submissions',
        submissions=submissions,
        status_counts=status_counts,
    )


@role_views.route('/role/admin/review-management', methods=['GET'])
def admin_review_management():
    assignments = ReviewAssignment.query.order_by(ReviewAssignment.assigned_at.desc()).limit(20).all()
    total_assignments = ReviewAssignment.query.count()
    reviewed = ReviewAssignment.query.join(ReviewAssignment.review).count()
    pending = total_assignments - reviewed
    return _render_role_page(
        'admin/admin_review_management.html',
        'Administrator - Review Management',
        'Administrator',
        'Review Management',
        assignments=assignments,
        total_assignments=total_assignments,
        reviewed=reviewed,
        pending=pending,
    )


@role_views.route('/role/admin/agenda-builder', methods=['GET'])
def admin_agenda_builder():
    sessions = Session.query.order_by(Session.date, Session.time_slot).all()
    approved_presentations = Presentation.query.filter_by(status='Approved').all()
    return _render_role_page(
        'admin/admin_agenda_builder.html',
        'Administrator - Agenda Builder',
        'Administrator',
        'Agenda Builder',
        sessions=sessions,
        approved_presentations=approved_presentations,
    )


@role_views.route('/role/admin/judging-results', methods=['GET'])
def admin_judging_results():
    judge_assignments = JudgeAssignment.query.order_by(JudgeAssignment.assigned_at.desc()).limit(30).all()
    total_scores = Score.query.count()
    avg_score = 0
    if total_scores:
        avg_score = db.session.query(db.func.avg((Score.research_quality + Score.clarity + Score.innovation + Score.response_to_questions + Score.overall_impact) / 5.0)).scalar() or 0
    top_presentation_scores = (
        db.session.query(
            Presentation.id,
            Presentation.type,
            db.func.avg((Score.research_quality + Score.clarity + Score.innovation + Score.response_to_questions + Score.overall_impact) / 5.0).label('average_score')
        )
        .join(JudgeAssignment, JudgeAssignment.presentation_id == Presentation.id)
        .join(Score, Score.judge_assignment_id == JudgeAssignment.id)
        .group_by(Presentation.id)
        .order_by(db.desc('average_score'))
        .limit(10)
        .all()
    )
    return _render_role_page(
        'admin/admin_judging_results.html',
        'Administrator - Judging & Results',
        'Administrator',
        'Judging & Results',
        judge_assignments=judge_assignments,
        total_scores=total_scores,
        avg_score=round(avg_score, 2),
        top_presentation_scores=top_presentation_scores,
    )


@role_views.route('/role/admin/reports-analytics', methods=['GET'])
def admin_reports_analytics():
    total_submissions = Submission.query.count()
    total_reviews = ReviewAssignment.query.count()
    total_presentations = Presentation.query.count()
    total_sessions = Session.query.count()
    return _render_role_page(
        'admin/admin_reports_analytics.html',
        'Administrator - Reports & Analytics',
        'Administrator',
        'Reports & Analytics',
        total_submissions=total_submissions,
        total_reviews=total_reviews,
        total_presentations=total_presentations,
        total_sessions=total_sessions,
    )


@role_views.route('/role/admin/settings', methods=['GET'])
def admin_settings():
    # Static settings values for display
    app_settings = {
        'conference_name': "UWI Research Awards & Festival",
        'conference_date': "2026-05-10 to 2026-05-13",
        'reviewers_per_submission': 3,
        'judging_criteria': [
            'Research Quality',
            'Clarity',
            'Innovation',
            'Overall Impact'
        ],
    }
    return _render_role_page(
        'admin/admin_settings.html',
        'Administrator - Settings',
        'Administrator',
        'Settings',
        app_settings=app_settings,
    )


# Usher
@role_views.route('/role/usher/my-sessions', methods=['GET'])
def usher_my_sessions():
    return _render_role_page(
        'usher/usher_my_sessions.html',
        'Usher - My Sessions',
        'Usher',
        'My Sessions',
    )


@role_views.route('/role/usher/check-in', methods=['GET'])
def usher_check_in():
    return _render_role_page(
        'usher/usher_check_in.html',
        'Usher - Check-In',
        'Usher',
        'Check-In',
    )


@role_views.route('/role/usher/search-attendees', methods=['GET'])
def usher_search_attendees():
    return _render_role_page(
        'usher/usher_search_attendees.html',
        'Usher - Search Attendees',
        'Usher',
        'Search Attendees',
    )

@role_views.route("/role/usher/checkin/<int:user_id>", methods=["POST"])
def toggle_checkin(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user.checked_in = not user.checked_in
    db.session.commit()
    return jsonify({"checked_in": user.checked_in})

@role_views.route('/role/usher/attendance-report', methods=['GET'])
def usher_attendance_report():
    return _render_role_page(
        'usher/usher_attendance_report.html',
        'Usher - Attendance Report',
        'Usher',
        'Attendance Report',
    )

