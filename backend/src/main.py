import logging
import os

import src.oidc.oidcAuthorize as oidcAuthorize

# from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import Configuration
from .v1.models import auth_model
from .v1.routes.alert_routes import router as alert_routes
from .v1.routes.basin_routes import router as basin_router

logging.getLogger("uvicorn").handlers.clear()  # removes duplicated logs
LOGGER = logging.getLogger()


api_prefix_v1 = Configuration.API_V1_STR

OpenAPIInfo = {
    "title": "River Forecasting Alert Authoring API",
    "version": "0.1.0",
    "description": "API for the River Forecasting Alert Authoring application",
}
tags_metadata = [
    {
        "name": "FastAPI template for quickstart openshift",
        "description": "A quickstart template for FastAPI with SQLAlchemy, Postgres",
    },
]

app = FastAPI(
    title=OpenAPIInfo["title"],
    version=OpenAPIInfo["version"],
    openapi_tags=tags_metadata,
    swagger_ui_init_oauth={
        # TODO: get client from env
        "clientId": Configuration.OIDC_CLIENT_ID,
        "appName": "Doc Tools",
        "usePkceWithAuthorizationCodeGrant": True,
        "useBasicAuthenticationWithAccessCodeGrant": False,
        "scopes": "openid email profile",
        "realm": "standard",
    },
)
origins: list[str] = [
    "http://localhost*",
    "http://localhost:4200",
    "https://nr-rfc-alertauthoring-*-frontend.apps.silver.devops.gov.bc.ca",
]

origins_regex: str = (
    "^https*\:\/\/nr-rfc-alertauthoring\-(\d)*\-frontend\.apps\.silver\.devops\.gov\.bc\.ca$"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origins_regex,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Route verification endpoints"}


@app.get("/auth_user", response_model=auth_model.User)
async def bar(token=Depends(oidcAuthorize.get_current_user)):
    return token


@app.get("/authorized", response_model=bool)
async def bar(is_authZ=Depends(oidcAuthorize.authorize)):
    return is_authZ


app.include_router(basin_router, prefix=api_prefix_v1 + "/basins", tags=["Basins"])
app.include_router(alert_routes, prefix=api_prefix_v1 + "/alerts", tags=["Alerts"])


# Define the filter
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] != "/"


# Add filter to the logger
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
