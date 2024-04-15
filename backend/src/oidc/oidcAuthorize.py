import logging
import re

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OpenIdConnect
from jose import jwt

from src.core.config import Configuration
from src.v1.models import auth_model

LOGGER = logging.getLogger(__name__)

LOGGER.debug(f"Configuration.OIDC_CLIENT_ID: {Configuration.OIDC_CLIENT_ID}")
LOGGER.debug(f"Configuration.OIDC_CLIENT_ID: {Configuration.OIDC_WELLKNOWN}")

oidc = OpenIdConnect(
    openIdConnectUrl=Configuration.OIDC_WELLKNOWN,
    scheme_name=Configuration.OIDC_CLIENT_ID,
)


async def get_current_user(bearerToken: str = Depends(oidc)) -> auth_model.User:
    """
    Consumes the access token if it exists, validates it and extracts the user
    information from it, returning that.

    :param bearerToken: The bearer token from the header
    :type bearerToken: str, optional
    :raises InvalidAuthorization: _description_
    :return: The user information that was extracted from the bearer token
    :rtype: auth_model.User
    """
    authorize(bearerToken)
    # make sure the authorization information is correctg
    try:
        # extract the token, ie remove Bearer string
        token = bearerToken.replace("Bearer ", "")

        # # getting the jwks_uri
        well_knowns = httpx.get(url=Configuration.OIDC_WELLKNOWN)
        well_knowns_data = well_knowns.json()
        jwks_url = well_knowns_data["jwks_uri"]
        LOGGER.debug(f"jwks_url: {jwks_url}")

        # # get the public key
        jwks_resp = httpx.get(url=jwks_url)
        jwks_key = jwks_resp.json()

        algorithm = jwt.get_unverified_header(token).get("alg")
        LOGGER.debug(f"algorithm: {algorithm}")

        decode_options = {"verify_signature": True}
        LOGGER.debug(f"client id: {Configuration.OIDC_CLIENT_ID}")
        payload = jwt.decode(
            token,
            jwks_key,
            audience=Configuration.OIDC_CLIENT_ID,
            algorithms=[algorithm],
            options=decode_options,
        )
        LOGGER.debug(f"payload: {payload}")
    except jwt.JWTError as e:
        raise InvalidAuthorization(detail=f"Could not validate credentials: {e}")
    except Exception as e:
        LOGGER.error(f"Error: {e}")
        raise

    print(f"token is: {token}")
    LOGGER.debug(f"oidc: {oidc}  {oidc.__call__}")
    return payload


async def authorize(user_payload: auth_model.User = Depends(get_current_user)) -> bool:
    """
    having successfully authenticated and retrieved a valid access token, this
    method will ensure that required roles are defined in the access token.


    :param user_payload: the user information extracted from the bearer token
    :type user_payload: auth_model.User, optional
    :raises HTTPException: _description_
    :raises InvalidAuthorization: _description_
    """
    is_authorized = False
    roles = re.split("\s+", Configuration.OIDC_REQUIRED_ROLES)
    roles_set = set(roles)
    LOGGER.debug(f"required roles: {roles_set}")
    LOGGER.debug(f"user_payload: {user_payload}")
    try:
        if user_payload is None:
            # Not authenticated with oauth2_scheme, maybe with other scheme?
            # Raise here, or check for other options, or allow a simpler version for the anonymous users
            raise HTTPException(status_code=403, detail="Not authenticated")
        LOGGER.debug(f"user_payload: {user_payload['client_roles']}")
        # user_roles = re.split("\s+", user_payload["client_roles"])
        user_roles_set = set(user_payload["client_roles"])
        LOGGER.debug(f"granted roles: {user_roles_set}")
        intersected = list(roles_set.intersection(user_roles_set))
        if intersected:
            is_authorized = True
        if not is_authorized:
            raise InvalidAuthorization(
                detail=f"User does not have the required roles: {roles}"
            )

    except jwt.JWTError as e:
        raise InvalidAuthorization(detail=f"Could not validate credentials: {e}")
    except Exception as e:
        LOGGER.error(f"Error: {e}")
        raise
    return is_authorized


class InvalidAuthorization(HTTPException):
    """
    Exception raised when the header doesn't have the correct authorization config
    ie... not authorized
    """

    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
