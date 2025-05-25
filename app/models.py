from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    activities = db.relationship('UserActivity', backref='actor', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    description = db.Column(db.String(240))
    parts = db.relationship('Part', backref='machine', lazy='dynamic')

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    part_number = db.Column(db.String(64), index=True, unique=True)
    total_received = db.Column(db.Integer, default=0)
    consumed = db.Column(db.Integer, default=0)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'))
    history = db.relationship('PartHistory', backref='part', lazy='dynamic')

    @property
    def available(self):
        return self.total_received - self.consumed

class PartHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'))
    action = db.Column(db.String(20))  # 'added' or 'consumed'
    quantity = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    notes = db.Column(db.String(240))

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))