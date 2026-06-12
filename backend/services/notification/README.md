# Notification service

Migrated from **GKNotificationService**. Mounted at `/notification`.

## Files
`models.py` (Notification) · `schemas.py` · `controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on `/notification/notifications` (search: title, message).
Legacy `from`/`to` columns are modelled as `fromUserId`/`toUserId`.

## Domain logic
- **NotificationController** defaults `isActive=true` on create.

## Tests
`tests/test_remaining_services.py` — `test_notifications`.
