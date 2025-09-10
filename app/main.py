from fastapi import FastAPI
from app.api.routes import router as api_router
from app.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Mount API routes
    app.include_router(api_router)

    # Optional: simple health route
    @app.get("/healthz", tags=["internal"])
    async def healthz():
        return {"status": "ok"}

    return app

app = create_app()