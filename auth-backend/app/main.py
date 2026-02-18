from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config   import settings
from app.database import Base, engine
from app.router   import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✓ Auth database ready  →  analyticsai_auth.db")
    print(f"✓ Frontend origin      →  {settings.frontend_origin}")
    print(f"✓ Google OAuth         →  {'configured' if settings.google_client_id else 'NOT configured (email auth only)'}")
    yield


app = FastAPI(
    title    = "AnalyticsAI Auth API",
    version  = "1.0.0",
    lifespan = lifespan,
    docs_url = "/docs",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,     
        "http://localhost:5173",        
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "service": "analyticsai-auth", "port": 8001}
