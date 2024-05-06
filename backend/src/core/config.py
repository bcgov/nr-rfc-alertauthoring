import logging
import os
from typing import Any, Dict, Optional

from pydantic import PostgresDsn

# from pydantic_settings import BaseSettings

LOGGER = logging.getLogger(__name__)


class Settings:
    API_V1_STR: str = "/api/v1"
    POSTGRES_SERVER: str = os.getenv("POSTGRES_HOST", "127.0.0.1:5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DATABASE", "postgres")
    # SQLALCHEMY_DATABASE_URI: PostgresDsn.build(
    #     scheme="postgresql",
    #     username=os.getenv("POSTGRES_USER", "postgres"),
    #     password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    #     host=os.getenv("POSTGRES_HOST", "127.0.0.1:5432"),
    #     path=f"/{os.getenv('POSTGRES_DB', 'postgres')}",
    # )
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = PostgresDsn.build(
        scheme="postgresql",
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        path=os.getenv("POSTGRES_DATABASE", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
    )
    DEFAULT_SCHEMA: str = "py_api"

    LOGGER.debug(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
    print(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")

    # OIDC_CONF_URL = "https://dev.loginproxy.gov.bc.ca/auth/realms/standard/.well-known/openid-configuration"
    OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID", "hydrological-alerting-5261")
    OIDC_WELLKNOWN = os.getenv(
        "OIDC_WELLKNOWN",
        "https://dev.loginproxy.gov.bc.ca/auth/realms/standard/.well-known/openid-configuration",
    )
    OIDC_REQUIRED_ROLES = os.getenv("OIDC_REQUIRED_ROLES", "editor")


# @validator("SQLALCHEMY_DATABASE_URI", pre=True)
def assemble_db_connection(v: Optional[str], values: Dict[str, Any]) -> Any:
    if isinstance(v, str):
        return v
    return PostgresDsn.build(
        scheme="postgresql",
        username=values.get("POSTGRES_USER"),
        password=values.get("POSTGRES_PASSWORD"),
        host=values.get("POSTGRES_SERVER"),
        path=f"/{values.get('POSTGRES_DB') or ''}",
    )


Configuration = Settings()
