---
ddx:
  id: FEAT-recipe-share
  depends_on:
    - recipe-app-prd
  status: draft
---

# Feature Specification: FEAT-recipe-share — Recipe Sharing

**Feature ID**: FEAT-recipe-share
**Status**: Draft
**Priority**: P0
**Owner**: Product team

## Overview

This feature enables home cooks to author and share original recipes with the community. Users compose recipes with ingredients and instructions, optionally attach photos, and publish for peer review via ratings and comments.

## Ideal Future State

A home cook opens the app, taps "Share Recipe," fills in title, ingredients, instructions, and optionally uploads a photo, then hits publish. The recipe immediately appears in their profile and the global feed. Community members can rate, comment, and save. The contributor sees engagement metrics.

## Problem Statement

- **Current situation**: Users can only browse and save recipes, not contribute
- **Pain points**: Passionate home cooks have nowhere to share; app lacks creator retention; community content is sparse
- **Desired outcome**: ≥ 500 community recipes by month 6; users spend ≥ 10 minutes post-launch exploring community content

## Functional Areas

| Area | User question or job | Feature responsibility |
|------|----------------------|------------------------|
| Authoring | "How do I post my recipe?" | Form for title, ingredients, instructions, photo |
| Visibility | "How do others see my recipe?" | Recipe appears in user profile and global feed |
| Feedback | "How do I know if others like my recipe?" | Display rating and comment counts on recipe cards |

## Requirements

### Functional Requirements by Area

#### Authoring (SHARE-01..04)

[SHARE-01]. Recipe author form MUST accept title (text, required), ingredients list (textarea, required), step-by-step instructions (textarea, required), optional recipe description (textarea), and optional photo (JPEG/PNG, ≤ 10MB).

[SHARE-02]. Form validation MUST require title and instructions before submit button enables. Form MUST reject empty ingredients list.

[SHARE-03]. Photo upload MUST resize images to 800x600px for storage. Original filename discarded; file renamed to `{uuid}.jpg`.

[SHARE-04]. Submit MUST create recipe record with author_id, creation timestamp, draft status initially, then transition to published on confirmation.

#### Visibility (SHARE-05..06)

[SHARE-05]. Published recipes MUST appear in the global recipe feed in reverse chronological order. Author's profile page MUST list all recipes they authored.

[SHARE-06]. Recipe detail page MUST display author name, creation date, ingredients, instructions, photo (if provided), and aggregate statistics (ratings count, comment count, save count).

#### Feedback (SHARE-07..08)

[SHARE-07]. Recipe card in feed MUST show author's name, title, thumbnail photo (if provided), average rating (e.g., "4.2 ★"), count of ratings, and count of comments.

[SHARE-08]. Tapping "Edit" on own recipe MUST allow author to modify title, ingredients, instructions, and description (not retroactively change photo). Changes apply immediately; edit history not tracked (v1).

### Acceptance Criteria

| Requirement | Scenario | Given | When | Then |
|-------------|----------|-------|------|------|
| SHARE-01 | User fills form | Recipe authoring page | User enters title, ingredients, instructions | Submit button enabled |
| SHARE-02 | User tries to submit incomplete form | Form with title only | User clicks submit | Error message "ingredients required" |
| SHARE-03 | User uploads photo | Upload input | User selects JPEG 2000x2000px, 8MB | Image resized to 800x600, upload succeeds |
| SHARE-04 | User publishes recipe | Filled form | User clicks "publish" | Recipe appears in feed with author name and current time |
| SHARE-05 | User views own profile | Authored ≥ 2 recipes | User navigates to profile | All authored recipes listed in reverse chronological order |
| SHARE-06 | User views recipe detail | Global feed | User taps recipe card | Detail page shows author, creation date, ingredients, instructions, ratings count, comments count |
| SHARE-07 | User browses feed | ≥ 3 published recipes | User views home feed | Each recipe card shows title, author, rating, comment count |
| SHARE-08 | Author edits own recipe | Published recipe | Author taps "edit", changes title, clicks save | Title updated, changes appear immediately in feed |

### Non-Functional Requirements

- **Performance**: Recipe form submit ≤ 2s end-to-end
- **Security**: Photo upload sanitized; JPEG/PNG only; exif metadata stripped
- **Scalability**: Supports 100 concurrent publishers without 400+ errors
- **Reliability**: Published recipes never lost; transient upload errors trigger client retry

## User Stories

- User story references would live in `docs/helix/01-frame/user-stories/`.

## Edge Cases and Error Handling

- **Large photo**: User uploads 50MB image → error "file too large, max 10MB"
- **Network failure during upload**: Error toast appears; user can retry without re-entering form
- **Duplicate title**: Allowed; no uniqueness constraint
- **Spam recipe**: Users can flag; flagged recipes hidden from feed (moderation review in v2)

## Success Metrics

- Recipes published per month ≥ 25 by month 3
- Average time-to-publish ≤ 3 minutes
- Form abandonment rate ≤ 30%

## Constraints and Assumptions

- Single photo per recipe (v1); no multi-photo support
- No draft saving; form data lost on navigation (v1)
- Authors cannot delete recipes once published (v1)

## Dependencies

- **Other features**: Ratings feature (FEAT-ratings), Comments feature (FEAT-comments)
- **External services**: Image storage (S3 or equivalent)
- **PRD requirements**: "Users can post recipes", "Users can view saved recipes"

## Out of Scope

- Bulk recipe import from CSV
- Recipe versioning / edit history
- Draft recipes
- Recipe deletion by author
- Collaborative recipe authoring

## Review Checklist

- [x] Overview connects to PRD requirement "Users can post recipes"
- [x] Ideal future state describes desired user-visible outcome
- [x] Problem statement describes what exists and what is broken
- [x] Functional areas mapped across authoring, visibility, feedback
- [x] Requirements testable and specific
- [x] Acceptance criteria cover happy paths, errors, edge cases
- [x] Non-functional requirements have numeric targets
- [x] Edge cases cover realistic failure scenarios
- [x] Success metrics specific to feature
- [x] Dependencies reference real artifacts
- [x] Out of scope excludes reasonable assumptions
- [x] No implementation details
- [x] Consistent with governing PRD
