from App.database import db

class TrackSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    
    submission = db.relationship('Submission', foreign_keys=[submission_id])
    track = db.relationship('Track', foreign_keys=[track_id])