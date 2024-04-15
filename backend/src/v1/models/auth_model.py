from typing import List, Optional

from pydantic import AnyUrl, EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel):
    exp: int = Field(
        nullable=False,
        description="The expiration date specifies how long the token will be valid. If a token with an expiration date is verified after its expiration date has passed, the token will be invalid.",
    )
    iat: int = Field(
        nullable=False,
        description="The issued at-date specifies the token's time of creation",
    )
    auth_time: int = Field(
        nullable=False, description="Time when the authentication occurred"
    )
    jti: str = Optional[
        Field(nullable=False, description="The javascript web token id")
    ]
    iss: AnyUrl = Optional[Field(description="Issuer")]
    aud: str = Optional[
        Field(description="Audience, application that is consuming the JWT")
    ]
    sub: str = Optional[Field(description="Subject")]
    typ: str = Optional[
        Field(
            description="(token type) claim is a string that indicates the type of the JWT."
        )
    ]
    azp: str = Field(
        description="Authorized party - the party to which the ID Token was issued"
    )
    session_state: str = Optional[
        Field(
            description="Optional parameter if the OpenID Connect check session extension is enabled."
        )
    ]
    scope: Optional[str] = Field(
        description="Space separated list of the requested scope values. Must include at least the openid value."
    )
    sid: str = Optional[Field(description="Session ID")]
    idir_user_guid: str = Field(description="GUID used for the user in the IDIR system")
    client_roles: List[str] = Field(
        description="List of roles to which the user belongs"
    )
    identity_provider: str = Field(
        description="The identity provider creates a JWT for us"
    )
    idir_username: str = Field(description="username in idir")
    email_verified: bool = Field(
        description="True if the e-mail address has been verified; otherwise false"
    )
    name: str = Field(description="Full name")
    preferred_username: str = Field(
        description="Shorthand name by which the End-User wishes to be referred to"
    )
    display_name: str = Field(
        description="The name of the user to display in the query logs"
    )
    given_name: str = Field(description="Given name(s) or first name(s)")
    family_name: str = Field(description="Surname(s) or last name(s)")
    email: EmailStr = Field(description="Preferred e-mail address of the user")
