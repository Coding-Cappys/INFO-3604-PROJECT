from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from .. import db
from ..models import Submission, JudgingScore
from .utils import parse_rating

judge_bp = Blueprint("judge", __name__)


JUDGE_VISIBLE_STATUSES = ["accepted", "accepted_oral", "accepted_poster", "scheduled"]


def judge_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("judge", "admin"):
            flash("Judge access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@judge_bp.route("/")
@login_required
@judge_required
def dashboard():
    accepted = Submission.query.filter(
        Submission.status.in_(JUDGE_VISIBLE_STATUSES)
    ).all()
    scored_ids = {s.submission_id for s in JudgingScore.query.filter_by(judge_id=current_user.id).all()}
    pending = [s for s in accepted if s.id not in scored_ids]
    scored = [s for s in accepted if s.id in scored_ids]
    oral = [s for s in pending if s.presentation_type == "oral"]
    poster = [s for s in pending if s.presentation_type == "poster"]
    return render_template("judge/dashboard.html", pending=pending, scored=scored,
                           oral=oral, poster=poster, scored_ids=scored_ids)


@judge_bp.route("/presentations/<int:submission_id>")
@login_required
@judge_required
def view_presentation(submission_id):
    sub = Submission.query.filter(
        Submission.id == submission_id,
        Submission.status.in_(JUDGE_VISIBLE_STATUSES)
    ).first_or_404()
    existing = JudgingScore.query.filter_by(judge_id=current_user.id, submission_id=submission_id).first()
    return render_template("judge/presentation_detail.html", submission=sub, score=existing)


@judge_bp.route("/presentations/<int:submission_id>/score", methods=["GET", "POST"])
@login_required
@judge_required
def score_presentation(submission_id):
    sub = Submission.query.filter(
        Submission.id == submission_id,
        Submission.status.in_(JUDGE_VISIBLE_STATUSES)
    ).first_or_404()
    score = JudgingScore.query.filter_by(judge_id=current_user.id, submission_id=submission_id).first()

    if request.method == "POST":
        if not score:
            score = JudgingScore(judge_id=current_user.id, submission_id=submission_id)
            db.session.add(score)
        score.research_quality = parse_rating(request.form.get("research_quality"))
        score.clarity = parse_rating(request.form.get("clarity"))
        score.innovation = parse_rating(request.form.get("innovation"))
        score.response_to_questions = parse_rating(request.form.get("response_to_questions"))
        score.overall_impact = parse_rating(request.form.get("overall_impact"))
        score.comments = request.form.get("comments", "").strip()
        score.status = "submitted"
        db.session.commit()
        flash("Judging score submitted successfully.", "success")
        return redirect(url_for("judge.dashboard"))
    return render_template("judge/score_form.html", submission=sub, score=score)


@judge_bp.route("/results")
@login_required
@judge_required
def results():
    submissions = Submission.query.filter(
        Submission.status.in_(JUDGE_VISIBLE_STATUSES)
    ).all()
    ranked = []
    for sub in submissions:
        scores = [s for s in sub.judging_scores if s.status == "submitted"]
        if scores:
            avg = sum(s.total_score for s in scores if s.total_score) / len(scores)
            ranked.append((sub, round(avg, 1)))
    ranked.sort(key=lambda x: x[1], reverse=True)
    my_scores = {s.submission_id: s for s in JudgingScore.query.filter_by(judge_id=current_user.id).all()}
    return render_template("judge/results.html", ranked=ranked, my_scores=my_scores)
