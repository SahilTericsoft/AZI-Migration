"""Azure Blob storage for file attachments (lab onboarding docs, etc.).

The upload goes to the configured container; the returned blob URL is what we
persist on the record. Credentials come from `AZURE_STORAGE_CONNECTION_STRING`
in the environment — when it's empty (e.g. local/dev), `is_configured()` is
False and callers should surface a 503 rather than attempt an upload.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException

from core.config import settings

ALLOWED_MIME = {"image/jpeg", "image/png", "application/pdf"}
MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def is_configured() -> bool:
    return bool(settings.azure_storage_connection_string)


def upload_attachment(
    data: bytes,
    filename: str,
    content_type: str | None,
    *,
    prefix: str = "",
) -> str:
    """Upload bytes to the lab-attachments container; return the blob URL."""
    if not is_configured():
        raise HTTPException(503, "Attachment storage is not configured.")
    if content_type not in ALLOWED_MIME:
        raise HTTPException(400, "Only JPEG, PNG and PDF files are allowed.")
    if len(data) > MAX_BYTES:
        raise HTTPException(400, "File exceeds the 5 MB limit.")

    # Imported lazily so the dependency is only needed where storage is enabled.
    from azure.storage.blob import BlobServiceClient, ContentSettings

    service = BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    )
    container = settings.azure_lab_attachments_container
    safe_name = filename.replace("/", "_")
    blob_name = f"{prefix.strip('/') + '/' if prefix else ''}{uuid.uuid4()}-{safe_name}"

    blob = service.get_blob_client(container=container, blob=blob_name)
    blob.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )
    return blob.url
