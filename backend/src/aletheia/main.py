from fastapi import FastAPI

from aletheia.core.errors import register_error_handlers
from aletheia.core.health import router as health_router
from aletheia.core.request_id import RequestIdMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="Aletheia API", version="0.1.0")
    app.add_middleware(RequestIdMiddleware)
    register_error_handlers(app)
    app.include_router(health_router)
    return app


app = create_app()
