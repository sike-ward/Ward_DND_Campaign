"""
MythosEngine FastAPI application.

Creates the FastAPI app, wires up AppContext, and registers all route
modules.  Uvicorn points at ``server.app:app``.

Start from the project root (the directory containing both
``MythosEngine/`` and ``server/``):

    uvicorn server.app:app --host 127.0.0.1 --port 8741 --reload

The Electron ``main.cjs`` starts this automatically in production.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from MythosEngine.config.config import Config
from MythosEngine.context.app_context import AppContext
from server.dependencies import set_app_context
from server.routes import ai, auth, dashboard, invites, notes, settings, users

logger = logging.getLogger(__name__)


# ── App lifespan ──────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Bootstrap AppContext once at server startup."""
    cfg = Config()
    ctx = AppContext(cfg)

    # Wire up AI engine if an API key is present
    api_key = getattr(cfg, "OPENAI_API_KEY", "")
    if api_key:
        try:
            from MythosEngine.ai.core.model_router import get_model_backend

            ctx.ai = get_model_backend(cfg, storage=ctx.storage)
            logger.info("AI engine initialised.")
        except Exception as exc:
            logger.warning("AI engine failed to initialise: %s", exc)

    set_app_context(ctx)
    logger.info("MythosEngine server ready. Vault: %s", getattr(cfg, "VAULT_PATH", "?"))
    yield
    logger.info("MythosEngine server shutting down.")


# ── FastAPI instance ──────────────────────────────────────────────────────────

app = FastAPI(
    title="MythosEngine API",
    version="1.0.0",
    description="REST API for the MythosEngine D&D campaign management platform.",
    lifespan=lifespan,
)

# Allow the Vite dev server (port 5173) and production Electron renderer
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8741",
        "http://127.0.0.1:8741",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(ai.router)
app.include_router(dashboard.router)
app.include_router(settings.router)
app.include_router(users.router)
app.include_router(invites.router)


# ── Health check ─────────────────────────────────────────────────────────────


@app.get("/health", tags=["health"])
def health():
    """Liveness probe used by the Electron launcher to detect API readiness."""
    return {"status": "ok", "service": "MythosEngine"}
