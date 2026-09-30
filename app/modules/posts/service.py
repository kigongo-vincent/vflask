"""Post service layer."""

from __future__ import annotations

from app.base.query import apply_filters
from app.extensions import db
from app.modules.posts.models import Post

FILTERABLE: set[str] = {
    "title",
    "caption",
    "attachment",
    "author",
}


class PostService:
    """Business logic for Post."""

    def __init__(self) -> None:
        self.db = db

    def list_posts(self, req: dict) -> tuple[list[Post], int]:
        """List posts with filtering and pagination."""
        pagination = req.get("pagination", {})
        page = pagination.get("page", 1)
        limit = pagination.get("limit", 10)

        query = self.db.session.query(Post)

        # Exclude soft-deleted by default
        if not any(f.get("column") == "trashed" for f in req.get("columns", [])):
            query = query.filter(Post.deleted_at.is_(None))

        # Apply filters
        query = apply_filters(query, Post, req.get("columns", []), FILTERABLE)

        # Search
        if req.get("search"):
            term = f"%{req['search']}%"
            query = query.filter(
                Post.title.like(term) |                Post.caption.like(term) |                Post.attachment.like(term) |                Post.author.like(term)            )

        total = query.count()
        rows = (
            query.order_by(Post.created_at.desc())
            .limit(limit)
            .offset((page - 1) * limit)
            .all()
        )
        return rows, total

    def get_post(self, item_id: int) -> Post | None:
        """Get a single post by ID."""
        return self.db.session.get(Post, item_id)

    def create_post(self, data: dict) -> Post:
        """Create a new post."""
        item = Post(**data)
        self.db.session.add(item)
        self.db.session.commit()
        return item

    def update_post(self, item_id: int, updates: dict) -> Post | None:
        """Update an existing post."""
        item = self.get_post(item_id)
        if not item or item.deleted_at:
            return None
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.db.session.commit()
        return item

    def delete_post(self, item_id: int) -> bool:
        """Soft delete a post."""
        item = self.get_post(item_id)
        if not item:
            return False
        item.soft_delete()
        self.db.session.commit()
        return True

    def bulk_delete(self, ids: list[int]) -> int:
        """Soft delete multiple posts."""
        count = 0
        for item in self.db.session.query(Post).filter(Post.id.in_(ids)):
            item.soft_delete()
            count += 1
        self.db.session.commit()
        return count