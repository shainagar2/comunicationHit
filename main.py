# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import inspect

from app.config import get_settings
from app.db import Base, engine
from app.api.routes import router as api_router
from app import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # עולה לפני שהאפליקציה זמינה
    print(">> Lifespan: creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(">> Lifespan: tables now:", tables)
    except Exception as e:
        print(">> Lifespan: create_all FAILED:", e)
    # מאפשר לשרת לעלות
    yield
    # נסגר כשכבים את השרת
    print(">> Lifespan: shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,  # מחליף on_event("startup")
    )

    # רישום הראוטרים של ה-API
    app.include_router(api_router)

    # בריאות בסיסי
    @app.get("/healthz", tags=["internal"])
    async def healthz():
        return {"status": "ok"}

    return app


app = create_app()


# אופציונלי: הרצה ישירה עם uvicorn ע"י `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

    # main.py
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5173"],  # לפי הפרונט
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

