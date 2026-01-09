"""JWT Token handling."""
import jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: datetime
    roles: list = []
    
class JWTHandler:
    def __init__(self, secret: str, algorithm: str = "HS256", expiry_minutes: int = 30):
        self.secret = secret
        self.algorithm = algorithm
        self.expiry_minutes = expiry_minutes
    
    def create_token(self, user_id: str, roles: list = None) -> str:
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self.expiry_minutes),
            "roles": roles or []
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[TokenPayload]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        payload = self.verify_token(token)
        if payload:
            return self.create_token(payload.sub, payload.roles)
        return None

def create_access_token(user_id: str, secret: str, roles: list = None, expiry_minutes: int = 30) -> str:
    handler = JWTHandler(secret, expiry_minutes=expiry_minutes)
    return handler.create_token(user_id, roles)

def verify_token(token: str, secret: str) -> Optional[TokenPayload]:
    handler = JWTHandler(secret)
    return handler.verify_token(token)
