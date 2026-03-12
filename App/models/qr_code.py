from App.database import db


class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    code = db.Column(db.String(256), nullable=False, unique=True)

    user = db.relationship('User', back_populates='qr_code')
