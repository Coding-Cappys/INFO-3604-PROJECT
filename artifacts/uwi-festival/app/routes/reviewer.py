from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from .. import db
from ..models import Submission, Review, ReviewerAssignment, User
from .utils import parse_rating

reviewer_bp = Blueprint("reviewer", __name__)


def reviewer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("reviewer", "admin"):
            flash("Reviewer access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@reviewer_bp.route("/")
@login_required
@reviewer_required
def dashboard():
    assignments = ReviewerAssignment.query.filter_by(reviewer_id=current_user.id).all()
    submission_ids = [a.submission_id for a in assignments]
    submissions = Submission.query.filter(Submission.id.in_(submission_ids)).all()
    reviewed_ids = {r.submission_id for r in Review.query.filter_by(reviewer_id=current_user.id).all()}
    pending = [s for s in submissions if s.id not in reviewed_ids]
    reviewed = [s for s in submissions if s.id in reviewed_ids]
    stats = {
        "total_assigned": len(submissions),
        "pending": len(pending),
        "reviewed": len(reviewed),
    }
    return render_template("reviewer/dashboard.html", pending=pending, reviewed=reviewed, stats=stats)


@reviewer_bp.route("/submissions/<int:submission_id>")
@login_required
@reviewer_required
def view_submission(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    assignment = ReviewerAssignment.query.filter_by(
        reviewer_id=current_user.id, submission_id=submission_id
    ).first()
    if not assignment and current_user.role != "admin":
        flash("You are not assigned to review this submission.", "danger")
        return redirect(url_for("reviewer.dashboard"))
    existing_review = Review.query.filter_by(
        reviewer_id=current_user.id, submission_id=submission_id
    ).first()
    return render_template("reviewer/submission_detail.html", submission=sub, review=existing_review)


@reviewer_bp.route("/submissions/<int:submission_id>/review", methods=["GET", "POST"])
@login_required
@reviewer_required
def write_review(submission_id):
    sub = Submission.query.get_or_404(submission_id)
    assignment = ReviewerAssignment.query.filter_by(
        reviewer_id=current_user.id, submission_id=submission_id
    ).first()
    if not assignment and current_user.role != "admin":
        flash("You are not assigned to review this submission.", "danger")
        return redirect(url_for("reviewer.dashboard"))

    review = Review.query.filter_by(reviewer_id=current_user.id, submission_id=submission_id).first()

    if request.method == "POST":
        if not review:
            review = Review(reviewer_id=current_user.id, submission_id=submission_id)
            db.session.add(review)

        review.research_quality = parse_rating(request.form.get("research_quality"))
        review.methodology = parse_rating(request.form.get("methodology"))
        review.relevance = parse_rating(request.form.get("relevance"))
        review.clarity = parse_rating(request.form.get("clarity"))
        review.overall_score = parse_rating(request.form.get("overall_score"))
        review.comments = request.form.get("comments", "").strip()
        review.recommendation = request.form.get("recommendation")
        review.status = "submitted"
        db.session.commit()
        flash("Review submitted successfully.", "success")
        return redirect(url_for("reviewer.dashboard"))
    return render_template("reviewer/write_review.html", submission=sub, review=review)


@reviewer_bp.route("/my-reviews")
@login_required
@reviewer_required
def my_reviews():
    reviews = Review.query.filter_by(reviewer_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template("reviewer/my_reviews.html", reviews=reviews)
