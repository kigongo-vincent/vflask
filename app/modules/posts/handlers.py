"""Post request handlers."""

from __future__ import annotations

from flask import request

from app.base import api_error, api_ok, paginated_response
from app.modules.posts.service import PostService


class PostHandler:
    """Handle HTTP requests for Post."""

    def __init__(self) -> None:
        self.service = PostService()

    def list(self) -> tuple:
        """List posts with pagination and filters."""
        req = request.get_json(silent=True) or {}
        if "pagination" not in req:
            return api_error("Invalid payload: pagination required")
        try:
            items, total = self.service.list_posts(req)
        except ValueError as e:
            return api_error(str(e))
        except Exception as e:
            return api_error(str(e), 500)
        return paginated_response(
            [i.to_dict() for i in items],
            total,
            req["pagination"]["page"],
            req["pagination"]["limit"],
        )

    def create(self) -> tuple:
        """Create a new post."""
        body = request.get_json(silent=True) or {}
        if not body:
            return api_error("Invalid payload")
        try:
            item = self.service.create_post(body)
        except Exception as e:
            return api_error(str(e), 500)
        return api_ok(item.to_dict(), msg="created", status=201)

    def get(self, item_id: int) -> tuple:
        """Get a single post."""
        item = self.service.get_post(item_id)
        if not item or item.deleted_at:
            return api_error("Post not found", 404)
        return api_ok(item.to_dict())

    def update(self, item_id: int) -> tuple:
        """Update a post."""
        body = request.get_json(silent=True) or {}
        item = self.service.update_post(item_id, body)
        if not item:
            return api_error("Post not found", 404)
        return api_ok(item.to_dict(), msg="updated")

    def delete(self, item_id: int) -> tuple:
        """Soft delete a post."""
        if not self.service.delete_post(item_id):
            return api_error("Post not found", 404)
        return api_ok(msg="deleted")

    def bulk_delete(self) -> tuple:
        """Soft delete multiple posts."""
        body = request.get_json(silent=True) or {}
        if "ids" not in body or not isinstance(body["ids"], list):
            return api_error("Invalid payload: ids array required")
        count = self.service.bulk_delete(body["ids"])
        return api_ok({"deleted": count}, msg="bulk deleted successfully")