from flask import Blueprint, render_template

role_views = Blueprint('role_views', __name__, template_folder='../templates')


def _render_role_page(template_name, title, role_label, page_title):
    return render_template(
        template_name,
        title=title,
        role_label=role_label,
        page_title=page_title,
    )


# Author
@role_views.route('/role/author/create-submission', methods=['GET'])
def author_create_submission():
    return _render_role_page(
        'author_create_submission.html',
        'Author - Create Submission',
        'Author',
        'Create Submission',
    )


@role_views.route('/role/author/my-submissions', methods=['GET'])
def author_my_submissions():
    return _render_role_page(
        'author_my_submissions.html',
        'Author - My Submissions',
        'Author',
        'My Submissions',
    )


@role_views.route('/role/author/status-tracking', methods=['GET'])
def author_status_tracking():
    return _render_role_page(
        'author_status_tracking.html',
        'Author - Status Tracking',
        'Author',
        'Status Tracking',
    )


@role_views.route('/role/author/reviewer-feedback', methods=['GET'])
def author_reviewer_feedback():
    return _render_role_page(
        'author_reviewer_feedback.html',
        'Author - Reviewer Feedback',
        'Author',
        'Reviewer Feedback',
    )


# Reviewer
@role_views.route('/role/reviewer/assigned-abstracts', methods=['GET'])
def reviewer_assigned_abstracts():
    return _render_role_page(
        'reviewer_assigned_abstracts.html',
        'Reviewer - Assigned Abstracts',
        'Reviewer',
        'Assigned Abstracts',
    )


@role_views.route('/role/reviewer/my-reviews', methods=['GET'])
def reviewer_my_reviews():
    return _render_role_page(
        'reviewer_my_reviews.html',
        'Reviewer - My Reviews',
        'Reviewer',
        'My Reviews',
    )


@role_views.route('/role/reviewer/guidelines', methods=['GET'])
def reviewer_guidelines():
    return _render_role_page(
        'reviewer_guidelines.html',
        'Reviewer - Guidelines',
        'Reviewer',
        'Guidelines',
    )


@role_views.route('/role/reviewer/statistics', methods=['GET'])
def reviewer_statistics():
    return _render_role_page(
        'reviewer_statistics.html',
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
        'attendee_schedule_agenda.html',
        'Attendee - Schedule & Agenda',
        'Attendee',
        'Schedule & Agenda',
    )


@role_views.route('/role/attendee/my-schedule', methods=['GET'])
def attendee_my_schedule():
    return _render_role_page(
        'attendee_my_schedule.html',
        'Attendee - My Schedule',
        'Attendee',
        'My Schedule',
    )


@role_views.route('/role/attendee/presentations', methods=['GET'])
def attendee_presentations():
    return _render_role_page(
        'attendee_presentations.html',
        'Attendee - Presentations',
        'Attendee',
        'Presentations',
    )


@role_views.route('/role/attendee/my-qr-code', methods=['GET'])
def attendee_my_qr_code():
    return _render_role_page(
        'attendee_my_qr_code.html',
        'Attendee - My QR Code',
        'Attendee',
        'My QR Code',
    )


@role_views.route('/role/attendee/qa-feedback', methods=['GET'])
def attendee_qa_feedback():
    return _render_role_page(
        'attendee_qa_feedback.html',
        'Attendee - Q&A & Feedback',
        'Attendee',
        'Q&A & Feedback',
    )


# Admin
@role_views.route('/role/admin/submissions', methods=['GET'])
def admin_submissions():
    return _render_role_page(
        'admin_submissions.html',
        'Administrator - Submissions',
        'Administrator',
        'Submissions',
    )


@role_views.route('/role/admin/review-management', methods=['GET'])
def admin_review_management():
    return _render_role_page(
        'admin_review_management.html',
        'Administrator - Review Management',
        'Administrator',
        'Review Management',
    )


@role_views.route('/role/admin/agenda-builder', methods=['GET'])
def admin_agenda_builder():
    return _render_role_page(
        'admin_agenda_builder.html',
        'Administrator - Agenda Builder',
        'Administrator',
        'Agenda Builder',
    )


@role_views.route('/role/admin/judging-results', methods=['GET'])
def admin_judging_results():
    return _render_role_page(
        'admin_judging_results.html',
        'Administrator - Judging & Results',
        'Administrator',
        'Judging & Results',
    )


@role_views.route('/role/admin/reports-analytics', methods=['GET'])
def admin_reports_analytics():
    return _render_role_page(
        'admin_reports_analytics.html',
        'Administrator - Reports & Analytics',
        'Administrator',
        'Reports & Analytics',
    )


@role_views.route('/role/admin/settings', methods=['GET'])
def admin_settings():
    return _render_role_page(
        'admin_settings.html',
        'Administrator - Settings',
        'Administrator',
        'Settings',
    )


# Usher
@role_views.route('/role/usher/my-sessions', methods=['GET'])
def usher_my_sessions():
    return _render_role_page(
        'usher_my_sessions.html',
        'Usher - My Sessions',
        'Usher',
        'My Sessions',
    )


@role_views.route('/role/usher/check-in', methods=['GET'])
def usher_check_in():
    return _render_role_page(
        'usher_check_in.html',
        'Usher - Check-In',
        'Usher',
        'Check-In',
    )


@role_views.route('/role/usher/search-attendees', methods=['GET'])
def usher_search_attendees():
    return _render_role_page(
        'usher_search_attendees.html',
        'Usher - Search Attendees',
        'Usher',
        'Search Attendees',
    )


@role_views.route('/role/usher/attendance-report', methods=['GET'])
def usher_attendance_report():
    return _render_role_page(
        'usher_attendance_report.html',
        'Usher - Attendance Report',
        'Usher',
        'Attendance Report',
    )
