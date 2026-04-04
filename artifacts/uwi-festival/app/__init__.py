import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///uwi_festival.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = True

    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.author import author_bp
    from .routes.reviewer import reviewer_bp
    from .routes.attendee import attendee_bp
    from .routes.judge import judge_bp
    from .routes.usher import usher_bp
    from .routes.public import public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(author_bp, url_prefix="/author")
    app.register_blueprint(reviewer_bp, url_prefix="/reviewer")
    app.register_blueprint(attendee_bp, url_prefix="/attendee")
    app.register_blueprint(judge_bp, url_prefix="/judge")
    app.register_blueprint(usher_bp, url_prefix="/usher")

    with app.app_context():
        db.create_all()
        _seed_initial_data()

    return app


def _seed_initial_data():
    from .models import User
    from werkzeug.security import generate_password_hash

    if User.query.count() == 0:
        users = [
            User(
                email="admin@uwi.edu",
                password_hash=generate_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                role="admin",
                affiliation="UWI",
                discipline="Administration",
                is_active=True,
            ),
            User(
                email="author@uwi.edu",
                password_hash=generate_password_hash("author123"),
                first_name="Jane",
                last_name="Smith",
                role="author",
                affiliation="UWI St. Augustine",
                discipline="Computer Science",
                is_active=True,
            ),
            User(
                email="reviewer@uwi.edu",
                password_hash=generate_password_hash("reviewer123"),
                first_name="Dr. Robert",
                last_name="Brown",
                role="reviewer",
                affiliation="UWI Mona",
                discipline="Engineering",
                is_active=True,
            ),
            User(
                email="attendee@uwi.edu",
                password_hash=generate_password_hash("attendee123"),
                first_name="Maria",
                last_name="Jones",
                role="attendee",
                affiliation="UWI Cave Hill",
                discipline="Biology",
                is_active=True,
            ),
            User(
                email="judge@uwi.edu",
                password_hash=generate_password_hash("judge123"),
                first_name="Prof. Alan",
                last_name="Carter",
                role="judge",
                affiliation="UWI St. Augustine",
                discipline="Physics",
                is_active=True,
            ),
            User(
                email="usher@uwi.edu",
                password_hash=generate_password_hash("usher123"),
                first_name="Sarah",
                last_name="Williams",
                role="usher",
                affiliation="UWI",
                discipline="",
                is_active=True,
            ),
        ]
        from . import db
        for u in users:
            db.session.add(u)
        db.session.commit()

        _seed_submissions()


def _seed_submissions():
    from .models import Submission, Review, ScheduledSession, Venue, Track, JudgingScore, ReviewerAssignment
    from . import db
    from .models import User

    track1 = Track(name="Computer Science & Engineering", description="Research in computing, AI, software, and engineering systems")
    track2 = Track(name="Life Sciences & Medicine", description="Research in biology, medicine, public health, and biomedical sciences")
    track3 = Track(name="Social Sciences & Humanities", description="Research in sociology, history, economics, and culture")
    db.session.add_all([track1, track2, track3])
    db.session.flush()

    venue1 = Venue(name="Main Auditorium", location="Block A, Ground Floor", capacity=300)
    venue2 = Venue(name="Seminar Room 1", location="Block B, First Floor", capacity=80)
    venue3 = Venue(name="Poster Hall", location="Student Activity Centre", capacity=200)
    db.session.add_all([venue1, venue2, venue3])
    db.session.flush()

    author = User.query.filter_by(role="author").first()
    reviewer = User.query.filter_by(role="reviewer").first()
    judge = User.query.filter_by(role="judge").first()

    submissions = [
        Submission(
            title="Advancing Neural Network Efficiency for Edge Computing Devices",
            authors="Jane Smith, Dr. Robert Brown",
            affiliation="UWI St. Augustine",
            abstract="This study presents a novel approach to compressing deep neural networks for deployment on resource-constrained edge devices while maintaining high accuracy. We explore quantization and pruning techniques applied to transformer-based models, demonstrating a 70% reduction in model size with less than 2% accuracy degradation across benchmark datasets. The proposed framework enables real-time inference on microcontroller units, opening new possibilities for IoT applications in developing regions.",
            keywords="neural networks, edge computing, model compression, IoT",
            track_id=track1.id,
            presentation_type="oral",
            status="accepted",
            author_id=author.id,
        ),
        Submission(
            title="Medicinal Plant Compounds as Antimicrobial Agents Against Drug-Resistant Bacteria",
            authors="Jane Smith",
            affiliation="UWI St. Augustine",
            abstract="This research investigates bioactive compounds extracted from five indigenous Caribbean plant species for antimicrobial activity against MRSA and multidrug-resistant E. coli. Using bioassay-guided fractionation and LC-MS analysis, we identified three novel flavonoids exhibiting significant antimicrobial properties. In vitro tests demonstrated minimum inhibitory concentrations comparable to established antibiotics. These findings suggest promising leads for the development of novel antimicrobial agents derived from regional biodiversity.",
            keywords="antimicrobial, medicinal plants, drug resistance, Caribbean flora",
            track_id=track2.id,
            presentation_type="poster",
            status="accepted",
            author_id=author.id,
        ),
        Submission(
            title="Economic Impact of Remote Work on Urban-Rural Migration Patterns in Trinidad",
            authors="Jane Smith, Maria Jones",
            affiliation="UWI St. Augustine",
            abstract="The post-pandemic shift to remote work has created new migration dynamics across the Caribbean. This study analyses census data and survey responses from 1,200 workers to quantify movement from urban centers to rural communities in Trinidad and Tobago between 2020-2025. Our findings reveal a 34% increase in rural residency among knowledge workers, with significant implications for housing markets, local economies, and infrastructure planning.",
            keywords="remote work, migration, urban planning, economic geography",
            track_id=track3.id,
            presentation_type="oral",
            status="under_review",
            author_id=author.id,
        ),
    ]
    db.session.add_all(submissions)
    db.session.flush()

    assignment = ReviewerAssignment(
        reviewer_id=reviewer.id,
        submission_id=submissions[0].id,
        assigned_theme=track1.name,
    )
    db.session.add(assignment)

    review = Review(
        submission_id=submissions[0].id,
        reviewer_id=reviewer.id,
        research_quality=4,
        methodology=5,
        relevance=4,
        clarity=4,
        overall_score=4,
        comments="Excellent work on model compression techniques. The quantization approach is novel and the results are impressive. Minor clarification needed on the specific microcontroller test environment.",
        recommendation="accept",
        status="submitted",
    )
    db.session.add(review)
    db.session.flush()

    session1 = ScheduledSession(
        submission_id=submissions[0].id,
        venue_id=venue1.id,
        session_date="2026-04-15",
        start_time="09:00",
        end_time="09:20",
        session_chair="Prof. Alan Carter",
        poster_board=None,
    )
    session2 = ScheduledSession(
        submission_id=submissions[1].id,
        venue_id=venue3.id,
        session_date="2026-04-15",
        start_time="11:00",
        end_time="13:00",
        session_chair=None,
        poster_board="A5",
    )
    db.session.add_all([session1, session2])
    db.session.flush()

    score = JudgingScore(
        submission_id=submissions[0].id,
        judge_id=judge.id,
        research_quality=5,
        clarity=4,
        innovation=5,
        response_to_questions=4,
        overall_impact=5,
        comments="Outstanding research with clear practical applications. The presentation was articulate and the methodology well-justified.",
        status="submitted",
    )
    db.session.add(score)

    db.session.commit()
