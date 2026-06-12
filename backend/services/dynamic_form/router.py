"""Dynamic form router — /dynamic-form/chats (form/chat definitions)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from services.dynamic_form import controller as c
from services.dynamic_form import schemas as s

router = APIRouter(prefix="/dynamic-form")
TAG = ["dynamic-form"]


@router.post("/chats", tags=TAG)
def add_chat(body: s.ChatCreate, db: Session = Depends(get_db)):
    return c.ChatController(db).create(body.model_dump(exclude_unset=True))


@router.post("/chats/list", tags=TAG)
def list_chats(body: ListIn, db: Session = Depends(get_db)):
    return c.ChatController(db).list(body)


@router.get("/chats/{chat_id}", tags=TAG)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    return c.ChatController(db).get(chat_id)


@router.put("/chats/{chat_id}", tags=TAG)
def edit_chat(chat_id: int, body: s.ChatUpdate, db: Session = Depends(get_db)):
    return c.ChatController(db).update(chat_id, body.model_dump(exclude_unset=True))


@router.delete("/chats/{chat_id}", tags=TAG)
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    return c.ChatController(db).delete(chat_id)
