from datetime import datetime, timedelta
import requests
from jose import jwt

from core.settings import settings
from schemas.user import TokenUserInfoSchema


class JWTManager:
    key: str = settings.auth.SECRET_KEY
    algorithm: str = settings.auth.ALGORITHM
    expire: int = settings.auth.TOKEN_EXPIRE_MINUTES

    def _find_public_key(self, kid, jwkeys) -> str | None:
        for key in jwkeys:
            if key["kid"] == kid:
                return key

    def generate_token(self, payload: TokenUserInfoSchema) -> str:
        to_encode = payload.model_dump()
        expire = datetime.now() + timedelta(minutes=self.expire)
        to_encode.update(exp=expire)
        encoded = jwt.encode(to_encode, self.key, algorithm=self.algorithm)
        return encoded

    def decode_token(self, token: str) -> dict:
        decoded = jwt.decode(token, self.key, algorithms=[self.algorithm])
        return decoded

    def validate_auth0_token(self, token: str) -> dict:
        jwks = requests.get(settings.auth0.JWKS_URL).json()
        unverified_header = jwt.get_unverified_header(token)
        public_key = self._find_public_key(unverified_header["kid"], jwks["keys"])
        decoded = jwt.decode(
            token,
            key=public_key,
            audience=settings.auth0.AUDIENCE,
            algorithms=["RS256"],
        )
        return decoded


jwt_auth = JWTManager()
