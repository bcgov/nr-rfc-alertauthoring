import logging
import os

# from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from .core.config import Configuration
from .oidc.oidc import get_oidc
from .v1.routes.alert_routes import router as alert_routes
from .v1.routes.basin_routes import router as basin_router

logging.getLogger("uvicorn").handlers.clear()  # removes duplicated logs
LOGGER = logging.getLogger()

config = Config(".env")

oidc = get_oidc()


# THIS WORKS IN CASE FUTURE ATTEMPTS AT OAUTH2 FAIL
# ----------------------------------------------------------

# want to auth with OpenIdConnect (OAuth2, authorization_code with PKCE)

# oauth2_oidc = OAuth2AuthorizationCodeBearer(
#     authorizationUrl="https://dev.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/auth",
#     tokenUrl="https://dev.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/token",
#     scheme_name="hydrological-alerting-5261",
# )


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
        "clientId": "hydrological-alerting-5261",
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
app.add_middleware(SessionMiddleware, secret_key="!secret")


# Add filter to the logger


@app.get("/")
async def root():
    return {"message": "Route verification endpoints"}


# @app.route("/login")
# async def login(request: Request):
#     # absolute url for callback
#     # we will define it below
#     redirect_uri = request.url_for("auth")
#     LOGGER.info(f"redirect_uri: {redirect_uri}")
#     return await oauth.bcgov_sso.authorize_redirect(request, redirect_uri)
#     # return await oauth.google.authorize_redirect(request, redirect_uri)


# @app.get("/auth")
# async def auth(request: Request):
#     LOGGER.debug("auth called")
#     try:
#         token = await oauth.bcgov_sso.authorize_access_token(request)
#         LOGGER.debug(fa."token: {token}")
#     except OAuthError as error:
#         return HTMLResponse(f"<h1>{error.error}</h1>")
#     user = token.get("userinfo")
#     if user:
#         request.session["user"] = dict(user)
#     return RedirectResponse(url="/")


# @app.get("/logout")
# async def logout(request: Request):
#     request.session.pop("user", None)
#     return RedirectResponse(url="/")


@app.get("/test_auth")
async def bar(token=Depends(oidc)):
    return token


app.include_router(basin_router, prefix=api_prefix_v1 + "/basins", tags=["Basins"])
app.include_router(alert_routes, prefix=api_prefix_v1 + "/alerts", tags=["Alerts"])


# Define the filter
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] != "/"


# Add filter to the logger
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
