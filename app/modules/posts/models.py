"""Post models."""

from __future__ import annotations

from app.extensions import db
from app.shared.mixins import SoftDeleteMixin, TimestampMixin


class Post(SoftDeleteMixin, TimestampMixin, db.Model):
    """Post model."""
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    caption = db.Column(db.String(255), nullable=True)
    attachment = db.Column(db.String(255), nullable=True)
    author = db.Column(db.String(255), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "caption": self.caption,
            "attachment": self.attachment,
            "author": self.author,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }