import logging

from fastapi.security import OpenIdConnect

LOGGER = logging.getLogger(__name__)


def get_oidc():
    oidc = OpenIdConnect(
        openIdConnectUrl="https://dev.loginproxy.gov.bc.ca/auth/realms/standard/.well-known/openid-configuration",
        scheme_name="test",
    )
    LOGGER.debug(f"oidc: {oidc}  {oidc.__call__}")

    return oidc
