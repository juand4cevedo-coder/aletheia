from fastapi import FastAPI

from aletheia.core.errors import register_error_handlers
from aletheia.core.health import router as health_router
from aletheia.core.request_id import RequestIdMiddleware
from aletheia.modules.cases.router import router as cases_router
from aletheia.modules.evidence.router import router as evidence_router
from aletheia.modules.identity.router import router as identity_router
from aletheia.modules.organizations.router import router as organizations_router

API_V1_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    app = FastAPI(title="Aletheia API", version="0.1.0")
    app.add_middleware(RequestIdMiddleware)
    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(identity_router, prefix=API_V1_PREFIX)
    app.include_router(organizations_router, prefix=API_V1_PREFIX)
    app.include_router(cases_router, prefix=API_V1_PREFIX)
    app.include_router(evidence_router, prefix=API_V1_PREFIX)
    return app


app = create_app()
