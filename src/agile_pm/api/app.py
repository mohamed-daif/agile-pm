"""FastAPI Application for Agile-PM."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agile_pm.api.routers import agents, tasks, sprints, memory, system
from agile_pm.api.middleware.logging import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Starting Agile-PM API...")
    yield
    print("Shutting down Agile-PM API...")

def create_app(title: str = "Agile-PM API", version: str = "1.0.0", debug: bool = False) -> FastAPI:
    application = FastAPI(
        title=title, version=version,
        description="AI-Powered Agile Project Management API",
        docs_url="/api/docs", redoc_url="/api/redoc",
        openapi_url="/api/openapi.json", lifespan=lifespan, debug=debug,
    )
    application.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"]
    )
    application.add_middleware(LoggingMiddleware)
    application.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
    application.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
    application.include_router(sprints.router, prefix="/api/v1/sprints", tags=["Sprints"])
    application.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
    application.include_router(system.router, prefix="/api/v1/system", tags=["System"])
    
    @application.get("/", tags=["Root"])
    async def root():
        return {"name": "Agile-PM API", "version": version, "docs": "/api/docs"}
    
    @application.get("/health", tags=["Health"])
    async def health():
        return {"status": "healthy"}
    
    return application

app = create_app()
