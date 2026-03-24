from App.database import db


class Editor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    assigned_track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=True)
    is_lead_editor = db.Column(db.Boolean, nullable=False, default=False)
    can_assign_reviewers = db.Column(db.Boolean, nullable=False, default=True)
    can_finalize_decisions = db.Column(db.Boolean, nullable=False, default=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship('User')
    assigned_track = db.relationship('Track')
