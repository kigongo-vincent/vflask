"""Post routes."""

from __future__ import annotations

from flask import Blueprint

from app.base import auth_required, role_required
from app.modules.posts.handlers import PostHandler

bp = Blueprint("posts", __name__, url_prefix="/api/v1/posts")
handler = PostHandler()


@bp.post("/list")
@auth_required
@role_required("admin")
def list_posts() -> tuple:
    """List posts."""
    return handler.list()


@bp.post("/")
@auth_required
@role_required("admin")
def create_post() -> tuple:
    """Create post."""
    return handler.create()


@bp.get("/<int:item_id>")
@auth_required
def get_post(item_id: int) -> tuple:
    """Get post by ID."""
    return handler.get(item_id)


@bp.put("/<int:item_id>")
@auth_required
@role_required("admin")
def update_post(item_id: int) -> tuple:
    """Update post."""
    return handler.update(item_id)


@bp.delete("/<int:item_id>")
@auth_required
@role_required("admin")
def delete_post(item_id: int) -> tuple:
    """Delete post."""
    return handler.delete(item_id)


@bp.post("/bulk-delete")
@auth_required
@role_required("admin")
def bulk_delete_posts() -> tuple:
    """Bulk delete posts."""
    return handler.bulk_delete()