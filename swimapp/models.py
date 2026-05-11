from datetime import datetime
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='viewer')  # admin, timekeeper, viewer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return str(self.id)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    event_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), default='Open')
    meet_name = db.Column(db.String(100), default='General Meet')
    heat = db.Column(db.String(20), default='Final')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    athletes = db.relationship('Athlete', backref='event', lazy=True, cascade='all, delete-orphan')


class Athlete(db.Model):
    __tablename__ = 'athletes'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    lane = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(50), default='')
    # time stored in seconds as float, None means DNS/not swum yet
    time = db.Column(db.Float, nullable=True)
    reaction_time = db.Column(db.Float, nullable=True)
    rank = db.Column(db.Integer, nullable=True)
    points = db.Column(db.Integer, default=0)

    def time_display(self):
        if self.time is None:
            return '--:--.--'
        mins = int(self.time // 60)
        secs = self.time % 60
        if mins > 0:
            return f'{mins}:{secs:05.2f}'
        return f'{secs:.2f}'

    def delta_display(self, leader_time):
        if self.time is None or leader_time is None:
            return '--'
        diff = self.time - leader_time
        if diff == 0:
            return '--'
        return f'+{diff:.2f}'

    def to_dict(self, leader_time=None):
        return {
            'id': self.id,
            'lane': self.lane,
            'name': self.name,
            'team': self.team,
            'time': self.time_display(),
            'time_raw': self.time,
            'reaction_time': f'{self.reaction_time:.2f}' if self.reaction_time else '--',
            'rank': self.rank or '--',
            'delta': self.delta_display(leader_time),
            'points': self.points,
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), default='')
    user_username = db.Column(db.String(80), default='system')
    action_details = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(10), default='INFO')   # INFO, WARN, HIGH
    status = db.Column(db.String(10), default='SUCCESS')  # SUCCESS, DENIED, ERROR


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    value = db.Column(db.String(200), default='')
