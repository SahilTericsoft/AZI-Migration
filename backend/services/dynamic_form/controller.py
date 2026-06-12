"""Controller for the Dynamic Form service (Chats)."""

from __future__ import annotations

from core.controller import BaseController
from services.dynamic_form.models import Chat


class ChatController(BaseController):
    model = Chat
    name = "Chat"
