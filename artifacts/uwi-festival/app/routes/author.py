from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from .. import db
from ..models import Submission, Track
from .utils import parse_int

author_bp = Blueprint("author", __name__)


def author_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("author", "admin"):
            flash("Author access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@author_bp.route("/")
@login_required
@author_required
def dashboard():
    submissions = Submission.query.filter_by(author_id=current_user.id).order_by(
        Submission.submitted_at.desc()
    ).all()
    stats = {
        "total": len(submissions),
        "under_review": sum(1 for s in submissions if s.status in ("under_review", "submitted", "resubmitted")),
        "accepted": sum(1 for s in submissions if "accepted" in s.status or s.status == "scheduled"),
        "changes_requested": sum(1 for s in submissions if s.status == "changes_requested"),
    }
    return render_template("author/dashboard.html", submissions=submissions, stats=stats)


@author_bp.route("/submissions/new", methods=["GET", "POST"])
@login_required
@author_required
def new_submission():
    tracks = Track.query.all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        authors = request.form.get("authors", "").strip()
        affiliation = request.form.get("affiliation", "").strip()
        abstract = request.form.get("abstract", "").strip()
        keywords = request.form.get("keywords", "").strip()
        track_id = request.form.get("track_id")
        presentation_type = request.form.get("presentation_type", "oral")
        parsed_track_id = parse_int(track_id, minimum=1)

        if not title or not abstract or not authors:
            flash("Title, authors, and abstract are required.", "danger")
            return render_template("author/submission_form.html", tracks=tracks, edit=False)

        sub = Submission(
            title=title,
            authors=authors,
            affiliation=affiliation,
            abstract=abstract,
            keywords=keywords,
            track_id=parsed_track_id,
            presentation_type=presentation_type if presentation_type in ("oral", "poster") else "oral",
            status="submitted",
            author_id=current_user.id,
        )
        db.session.add(sub)
        db.session.commit()
        flash("Submission created successfully!", "success")
        return redirect(url_for("author.dashboard"))
    return render_template("author/submission_form.html", tracks=tracks, edit=False, submission=None)


@author_bp.route("/submissions/<int:submission_id>")
@login_required
@author_required
def submission_detail(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    if sub.author_id != current_user.id and current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("author.dashboard"))
    return render_template("author/submission_detail.html", submission=sub)


@author_bp.route("/submissions/<int:submission_id>/edit", methods=["GET", "POST"])
@login_required
@author_required
def edit_submission(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    if sub.author_id != current_user.id and current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("author.dashboard"))
    if sub.status not in ("submitted", "changes_requested", "draft"):
        flash("Cannot edit a submission that is under review or decided.", "warning")
        return redirect(url_for("author.submission_detail", submission_id=submission_id))

    tracks = Track.query.all()
    if request.method == "POST":
        sub.title = request.form.get("title", sub.title).strip()
        sub.authors = request.form.get("authors", sub.authors).strip()
        sub.affiliation = request.form.get("affiliation", "").strip()
        sub.abstract = request.form.get("abstract", sub.abstract).strip()
        sub.keywords = request.form.get("keywords", "").strip()
        track_id = parse_int(request.form.get("track_id"), minimum=1)
        sub.track_id = track_id
        presentation_type = request.form.get("presentation_type", sub.presentation_type)
        sub.presentation_type = presentation_type if presentation_type in ("oral", "poster") else sub.presentation_type
        sub.revision_notes = request.form.get("revision_notes", "").strip()
        if sub.status == "changes_requested":
            sub.status = "under_review"
        db.session.commit()
        flash("Submission updated successfully.", "success")
        return redirect(url_for("author.submission_detail", submission_id=submission_id))
    return render_template("author/submission_form.html", tracks=tracks, edit=True, submission=sub)
