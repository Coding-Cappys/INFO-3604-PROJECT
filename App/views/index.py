from flask import Blueprint, jsonify, render_template, request

from App.controllers import initialize, latest_submission_version
from App.models import Award, Digest, Presentation, PresentationStatus, Session

index_views = Blueprint("index_views", __name__, template_folder="../templates")


@index_views.route("/", methods=["GET"])
def index_page():
    sessions = Session.query.order_by(Session.date, Session.time_slot).limit(4).all()
    presentations = (
        Presentation.query.filter(
            Presentation.status.in_(
                [
                    PresentationStatus.Scheduled.value,
                    PresentationStatus.Scored.value,
                    PresentationStatus.AwardWinner.value,
                ]
            )
        )
        .order_by(Presentation.id.desc())
        .limit(6)
        .all()
    )
    awards = Award.query.order_by(Award.name).limit(4).all()
    latest_digest = Digest.query.order_by(Digest.year.desc(), Digest.id.desc()).first()
    stats = {
        "sessions": Session.query.count(),
        "presentations": Presentation.query.count(),
        "awards": Award.query.count(),
    }
    return render_template(
        "index.html",
        sessions=sessions,
        presentations=presentations,
        awards=awards,
        latest_digest=latest_digest,
        stats=stats,
    )


@index_views.route("/schedule", methods=["GET"])
def public_schedule():
    sessions = Session.query.order_by(Session.date, Session.time_slot).all()
    return render_template("public/public_schedule.html", sessions=sessions)


@index_views.route("/presentations", methods=["GET"])
def public_presentations():
    filter_type = request.args.get("type")
    query = Presentation.query.filter(
        Presentation.status.in_(
            [
                PresentationStatus.Scheduled.value,
                PresentationStatus.Scored.value,
                PresentationStatus.AwardWinner.value,
            ]
        )
    )
    if filter_type in {"Oral", "Poster"}:
        query = query.filter(Presentation.type == filter_type)
    presentations = query.order_by(Presentation.id.desc()).all()
    return render_template(
        "public/public_presentations.html",
        presentations=presentations,
        filter_type=filter_type,
        latest_submission_version=latest_submission_version,
    )


@index_views.route("/presentations/<int:presentation_id>", methods=["GET"])
def public_presentation_detail(presentation_id):
    presentation = Presentation.query.get_or_404(presentation_id)
    if presentation.status.value not in {
        PresentationStatus.Scheduled.value,
        PresentationStatus.Scored.value,
        PresentationStatus.AwardWinner.value,
    }:
        return render_template("401.html", error="Presentation is not publicly available."), 404

    related_query = Presentation.query.join(Presentation.submission).filter(
        Presentation.id != presentation.id,
        Presentation.status.in_(
            [
                PresentationStatus.Scheduled.value,
                PresentationStatus.Scored.value,
                PresentationStatus.AwardWinner.value,
            ]
        ),
    )
    if presentation.session_id:
        related_query = related_query.filter(Presentation.session_id == presentation.session_id)
    related_presentations = related_query.limit(4).all()
    return render_template(
        "public/public_presentation_detail.html",
        presentation=presentation,
        latest_version=latest_submission_version(presentation.submission) if presentation.submission else None,
        related_presentations=related_presentations,
    )


@index_views.route("/digest", methods=["GET"])
def public_digest():
    digests = Digest.query.order_by(Digest.year.desc(), Digest.id.asc()).all()
    return render_template("public/public_digest.html", digests=digests)


@index_views.route("/awards", methods=["GET"])
def public_awards():
    awarded_presentations = Presentation.query.filter(Presentation.award_id.isnot(None)).all()
    return render_template("public/public_awards.html", awarded_presentations=awarded_presentations)


@index_views.route("/init", methods=["GET"])
def init():
    initialize()
    return jsonify(message="db initialized!")


@index_views.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})
