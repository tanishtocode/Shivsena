from flask_login import UserMixin
from .. import db
from datetime import datetime


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id          = db.Column(db.Integer, primary_key=True)
    ticket_id   = db.Column(db.String(20), unique=True, nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    phone       = db.Column(db.String(15), nullable=False)
    email       = db.Column(db.String(100), nullable=True)
    address     = db.Column(db.String(200), nullable=False)
    category    = db.Column(db.String(50), nullable=False)
    location    = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority    = db.Column(db.String(10), nullable=False)
    status      = db.Column(db.String(20), default='Pending')
    photo       = db.Column(db.String(200), nullable=True)
    admin_note  = db.Column(db.Text, nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Complaint {self.ticket_id}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    is_admin   = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


class SocialWorkImage(db.Model):
    __tablename__ = 'social_work_images'

    id              = db.Column(db.Integer, primary_key=True)
    image_file      = db.Column(db.String(255), nullable=False)
    title           = db.Column(db.String(150), nullable=True)
    description     = db.Column(db.Text, nullable=True)
    event_date      = db.Column(db.String(50), nullable=True)

    # ── NEW FIELDS ──────────────────────────────────────
    media_type      = db.Column(db.String(10), default='image')   # 'image' | 'video'
    show_on_slider  = db.Column(db.Boolean, default=False)         # show on homepage slider
    is_featured     = db.Column(db.Boolean, default=False)         # mark as featured
    display_order   = db.Column(db.Integer, default=0)             # sort order (lower = first)
    # ────────────────────────────────────────────────────

    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SocialWorkImage {self.title or self.image_file}>'