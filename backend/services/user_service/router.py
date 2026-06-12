"""User service router — aggregates this service's sub-routers.

`main.py` includes this single router under the API prefix.
"""

from __future__ import annotations

from fastapi import APIRouter

from services.user_service.access_control import router as access_control_router
from services.user_service.auth import router as auth_router
from services.user_service.static_data import router as static_data_router
from services.user_service.users import router as users_router

router = APIRouter(prefix="/user-service")
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(access_control_router)
router.include_router(static_data_router)
