from fastapi import FastAPI

from liuliangchuhai.bootstrap.container import build_container
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.presentation.http.router import create_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    container = build_container(resolved_settings)
    app = FastAPI(title="liuliangchuhai API", version="0.1.0")
    app.include_router(create_router(container.get_system_status))
    return app
