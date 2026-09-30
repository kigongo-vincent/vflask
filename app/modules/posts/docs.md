# Post Module

Auto-generated documentation for the `posts` module.

## Model

**Post**

| Field | Type | Nullable | Unique | Index |
|-------|------|----------|--------|-------|
| id | Integer | No | Yes | Yes |
| title | string | Yes | No | No |
| caption | string | Yes | No | No |
| attachment | string | Yes | No | No |
| author | string | Yes | No | No |
| created_at | DateTime | No | No | No |
| updated_at | DateTime | No | No | No |
| deleted_at | DateTime | Yes | No | No |

## Endpoints

| Method | Path | Auth | Roles | Description |
|--------|------|------|-------|-------------|
| POST | `/api/v1/posts/list` | ✅ | admin | List posts |
| POST | `/api/v1/posts/` | ✅ | admin | Create post |
| GET | `/api/v1/posts/<id>` | ✅ | Any | Get post |
| PUT | `/api/v1/posts/<id>` | ✅ | admin | Update post |
| DELETE | `/api/v1/posts/<id>` | ✅ | admin | Delete post |
| POST | `/api/v1/posts/bulk-delete` | ✅ | admin | Bulk delete |

## Usage Examples

```bash
# List posts
curl -X POST http://localhost:5000/api/v1/posts/list \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"pagination": {"page": 1, "limit": 10}, "columns": [], "search": ""}'

# Create post
curl -X POST http://localhost:5000/api/v1/posts/ \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{ "title": ..., "caption": ..., "attachment": ..., "author": ... }'