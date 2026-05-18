---
ddx:
  id: TD-recipe-store
  depends_on:
    - FEAT-recipe-share
    - ADR-001
  status: draft
---

# Technical Design: TD-recipe-store

**Feature**: FEAT-recipe-share | **Related**: ADR-001 (SQLite) | **User Story**: Sharing recipes

## Scope

- Story-level design artifact for recipe storage and retrieval
- Covers database schema, API endpoints, and image storage integration
- Inherits single-writer SQLite constraint from ADR-001
- Governing artifacts: FEAT-recipe-share, ADR-001

## Acceptance Criteria

1. **Given** a user submits recipe form, **When** API receives request, **Then** recipe saved to `recipes` table with all fields populated
2. **Given** a recipe with photo, **When** file uploaded, **Then** resized image stored and filename recorded in recipe record
3. **Given** published recipes exist, **When** GET `/api/v1/recipes` called, **Then** returns JSON array ordered by creation_date DESC with ≤ 100 records per page

## Technical Approach

**Strategy**: RESTful API for recipe CRUD operations; SQLite for relational storage; external S3-compatible service for image storage; recipes served read-mostly (cache-friendly).

**Key Decisions**:
- Use SQLite tables for normalized schema (recipes, ratings, comments); foreign keys enforce referential integrity
- Store recipe photos in S3 with public read ACL; store filename reference in recipe record
- API returns paginated results (default 20 per page); sorting by creation_date for trending
- No in-process caching (v1); CDN caching via Cache-Control headers

**Trade-offs**:
- Normalized schema = referential integrity, slower joins | de-normalized = faster queries, stale data risk
- External image storage = decoupled scaling, S3 dependency | embedded images = tight coupling, larger database

## Component Changes

### Modified: API Layer
- **Current State**: Endpoints exist for user auth, recipe browsing (read-only)
- **Changes**: Add POST /api/v1/recipes (create recipe), PUT /api/v1/recipes/{id} (update), DELETE /api/v1/recipes/{id} (delete photo)
- **Files**: `src/api/recipes.ts`, `src/middleware/auth.ts` (add owner validation)

### New: Storage Service
- **Purpose**: Encapsulate image resizing and S3 uploads
- **Interfaces**: 
  - Input: File buffer, metadata (recipe_id)
  - Output: Public S3 URL, filename
- **Files**: `src/services/storage.ts`, `tests/unit/storage.test.ts`

### New: Database Schema
- **Purpose**: Define tables and relationships for recipe persistence
- **Files**: `migrations/001_create_recipes_schema.sql`

## API/Interface Design

```yaml
# Create Recipe
endpoint: /api/v1/recipes
method: POST
auth: Bearer token (required)
request:
  type: object
  properties:
    title: string (required, max 255)
    ingredients: string (required)
    instructions: string (required)
    description: string (optional, max 500)
    photo: file (optional, JPEG/PNG, ≤10MB)
response:
  type: object
  properties:
    id: uuid
    title: string
    author_id: uuid
    created_at: ISO8601
    photo_url: string (or null)
    status: string ("published")

# Get Recipe
endpoint: /api/v1/recipes/{id}
method: GET
response: { full recipe object with stats }

# List Recipes
endpoint: /api/v1/recipes
method: GET
query:
  limit: int (default 20, max 100)
  offset: int (default 0)
response:
  type: object
  properties:
    recipes: array of recipe objects
    total: int (total count)
    hasMore: boolean
```

## Data Model Changes

```sql
CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    description VARCHAR(500),
    photo_filename VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'published'
);

CREATE INDEX idx_recipes_author_id ON recipes(author_id);
CREATE INDEX idx_recipes_created_at ON recipes(created_at DESC);
```

## Integration Points

| From | To | Method | Data |
|------|-----|--------|------|
| API Layer | Storage Service | Function call | File buffer + metadata |
| Storage Service | S3 | HTTP PUT | Image bytes |
| API Layer | SQLite | SQL query | Recipe insert/select/update |

### External Dependencies
- **AWS S3** (or equivalent): Image storage | Fallback: None; user directed to retry
- **SQLite**: Local database file | Fallback: Not applicable (core dependency)

## Security

- **Authentication**: API requires Bearer token in Authorization header; recipes require user_id from token
- **Authorization**: Users can edit/delete only their own recipes; checked before mutation
- **Data Protection**: Photos exif metadata stripped; filename randomized; ACL set to public-read
- **Threats**: 
  - SQL injection: Use parameterized queries
  - CSRF: API token validation; no cookie-based auth
  - Oversized uploads: File size validated pre-upload (10MB max)

## Performance

- **Expected Load**: ≤ 20 recipe submissions per minute; ≤ 1000 concurrent reads
- **Response Target**: GET /recipes ≤ 100ms p99; POST /recipes ≤ 500ms p99
- **Optimizations**: Index on creation_date and author_id; paginate results; set Cache-Control max-age=300 for recipe detail

## Testing

- [ ] **Unit**: StorageService resizes photos to 800x600; rejects oversized files; strips exif
- [ ] **Integration**: API creates recipe record with all fields; photo URL stored; GET returns identical recipe
- [ ] **API**: POST /recipes with valid payload returns 201; GET /recipes?limit=5 returns ≤5 results
- [ ] **Security**: Authorization checks prevent cross-user edit; oversized upload returns 413 Payload Too Large

## Migration & Rollback

- **Backward Compatibility**: New API endpoints don't affect existing read-only endpoints
- **Data Migration**: None (new feature, fresh tables)
- **Feature Toggle**: None (MVP, feature ships on deploy)
- **Rollback**: Delete recipe records; drop tables via migration

## Implementation Sequence

1. Create database schema and migration — Files: `migrations/001_*` — Tests: schema validation
2. Implement StorageService with photo resizing — Files: `src/services/storage.ts` — Tests: unit tests for resize/exif
3. Implement API endpoints (POST, PUT, GET, DELETE) — Files: `src/api/recipes.ts` — Tests: integration tests
4. Wire endpoints into auth middleware and router — Files: `src/app.ts` — Tests: end-to-end API tests
5. Integrate photo upload with storage service — Tests: verify S3 URLs returned and stored

**Prerequisites**: User authentication and SQLite initialization must complete first (existing)

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Photo resizing fails on unusual image formats | Low | Medium | Validate format before resizing; add error handling with user message |
| S3 credentials expire or bucket deleted | Low | High | Store creds in env vars with rotation policy; monitor S3 health |
| SQLite write lock during high-concurrency upload | Medium | Medium | Implement write queue; monitor lock contention; plan Postgres migration |

## Review Checklist

- [x] Acceptance criteria use Given/When/Then and are verifiable
- [x] Technical approach inherits from ADR-001 (SQLite)
- [x] Key decisions have documented rationale
- [x] Trade-offs explicit (normalized vs denormalized schema)
- [x] Component changes clearly describe current vs new
- [x] API/interface design includes request/response schemas
- [x] Data model includes migration SQL
- [x] Integration points specify S3 fallback
- [x] Security covers auth, authz, data protection, threats
- [x] Performance targets numeric and specific
- [x] Testing covers unit, integration, API, security scenarios
- [x] Migration and rollback strategy documented
- [x] Implementation sequence ordered with file paths and test paths
- [x] Consistent with FEAT-recipe-share and ADR-001
