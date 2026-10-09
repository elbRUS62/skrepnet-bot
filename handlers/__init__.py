from aiogram import Router

from .start import router as start_router
from .subscription import router as subscription_router
from .donate import router as donate_router
from .connect import router as connect_router
from .admin import router as admin_router
from .changelog import router as changelog_router
from .invite import router as invite_router

router = Router()
router.include_router(start_router)
router.include_router(subscription_router)
router.include_router(donate_router)
router.include_router(connect_router)
router.include_router(admin_router)
router.include_router(changelog_router)
router.include_router(invite_router)