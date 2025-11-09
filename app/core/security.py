from datetime import datetime, timedelta
from typing import Optional, Any
from passlib.context import CryptContext
from jose import JWTError, jwt

from core.configs import get_settings

# Контекст для хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        return pwd_context.needs_update(hashed_password)

    @staticmethod
    def validate_strength(password: str) -> tuple[bool, Optional[str]]:
        if len(password) < 8:
            return False, "Пароль має містити мінімум 8 символів"

        if not any(c.isupper() for c in password):
            return False, "Пароль має містити хоча б одну велику літеру"

        if not any(c.islower() for c in password):
            return False, "Пароль має містити хоча б одну маленьку літеру"

        if not any(c.isdigit() for c in password):
            return False, "Пароль має містити хоча б одну цифру"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Пароль має містити хоча б один спецсимвол"

        return True, None


class JWTManager:
    def __init__(self):
        self.settings = get_settings()

    def create_access_token(
            self,
            subject: str | int,
            additional_claims: Optional[dict[str, Any]] = None
    ) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=self.settings.jwt.access_token_expire_minutes
        )

        to_encode = {
            "sub": str(subject),
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow(),
        }

        if additional_claims:
            to_encode.update(additional_claims)

        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.jwt.secret_key,
            algorithm=self.settings.jwt.algorithm
        )

        return encoded_jwt

    def create_refresh_token(
            self,
            subject: str | int,
            additional_claims: Optional[dict[str, Any]] = None
    ) -> str:
        expire = datetime.utcnow() + timedelta(
            days=self.settings.jwt.refresh_token_expire_days
        )

        to_encode = {
            "sub": str(subject),
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow(),
        }

        if additional_claims:
            to_encode.update(additional_claims)

        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.jwt.secret_key,
            algorithm=self.settings.jwt.algorithm
        )

        return encoded_jwt

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt.secret_key,
                algorithms=[self.settings.jwt.algorithm]
            )
            return payload
        except JWTError as e:
            raise JWTError(f"Invalid token: {str(e)}")

    def verify_token_type(self, payload: dict[str, Any], expected_type: str) -> bool:
        token_type = payload.get("type")
        return token_type == expected_type

    def get_token_subject(self, payload: dict[str, Any]) -> str:
        return payload.get("sub")

    def is_token_expired(self, payload: dict[str, Any]) -> bool:
        exp = payload.get("exp")
        if not exp:
            return True
        return datetime.utcnow() > datetime.fromtimestamp(exp)


class TokenHasher:
    @staticmethod
    def hash_token(token: str) -> str:
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def verify_token(token: str, hashed_token: str) -> bool:
        return TokenHasher.hash_token(token) == hashed_token


# Singleton екземпляри
_password_hasher: Optional[PasswordHasher] = None
_jwt_manager: Optional[JWTManager] = None
_token_hasher: Optional[TokenHasher] = None


def get_password_hasher() -> PasswordHasher:
    global _password_hasher
    if _password_hasher is None:
        _password_hasher = PasswordHasher()
    return _password_hasher


def get_jwt_manager() -> JWTManager:
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = JWTManager()
    return _jwt_manager


def get_token_hasher() -> TokenHasher:
    global _token_hasher
    if _token_hasher is None:
        _token_hasher = TokenHasher()
    return _token_hasher