from typing import Any, Optional
from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    def __init__(
            self,
            status_code: int,
            detail: str,
            headers: Optional[dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationException(BaseAppException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class InvalidCredentialsException(AuthenticationException):
    def __init__(self):
        super().__init__(detail="Невірний email або пароль")


class TokenExpiredException(AuthenticationException):
    def __init__(self):
        super().__init__(detail="Токен прострочений")


class InvalidTokenException(AuthenticationException):
    def __init__(self):
        super().__init__(detail="Невалідний токен")


class TokenRevokedException(AuthenticationException):
    def __init__(self):
        super().__init__(detail="Токен відкликаний")


# Винятки авторизації
class AuthorizationException(BaseAppException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class InsufficientPermissionsException(AuthorizationException):
    def __init__(self, required_permission: Optional[str] = None):
        detail = "Недостатньо прав для виконання цієї дії"
        if required_permission:
            detail = f"Потрібен дозвіл: {required_permission}"
        super().__init__(detail=detail)


class AccountBlockedException(AuthorizationException):
    def __init__(self, reason: Optional[str] = None):
        detail = "Ваш акаунт заблокований"
        if reason:
            detail = f"Ваш акаунт заблокований. Причина: {reason}"
        super().__init__(detail=detail)


class AccountNotVerifiedException(AuthorizationException):
    def __init__(self):
        super().__init__(detail="Потрібна верифікація email")


class UserException(BaseAppException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(UserException):
    def __init__(self, identifier: Optional[str] = None):
        detail = "Користувача не знайдено"
        if identifier:
            detail = f"Користувача з ідентифікатором '{identifier}' не знайдено"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserAlreadyExistsException(UserException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Користувач з email '{email}' вже існує"
        )


class UsernameAlreadyExistsException(UserException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{username}' вже зайнятий"
        )


class RoleException(BaseAppException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class RoleNotFoundException(RoleException):
    def __init__(self, role_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Роль '{role_name}' не знайдено"
        )


class RoleAlreadyExistsException(RoleException):
    def __init__(self, role_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Роль '{role_name}' вже існує"
        )


class SystemRoleException(RoleException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не можна модифікувати системну роль"
        )


class PermissionException(BaseAppException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class PermissionNotFoundException(PermissionException):
    def __init__(self, permission_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дозвіл '{permission_name}' не знайдено"
        )


class ValidationException(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class WeakPasswordException(ValidationException):
    def __init__(self):
        super().__init__(
            detail="Пароль має містити мінімум 8 символів, велику літеру, цифру та спецсимвол"
        )


class OAuthException(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class OAuthProviderException(OAuthException):
    def __init__(self, provider: str, error: str):
        super().__init__(detail=f"Помилка {provider}: {error}")


class TwoFactorException(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class Invalid2FACodeException(TwoFactorException):
    def __init__(self):
        super().__init__(detail="Невірний код двофакторної аутентифікації")


class TwoFactorRequiredException(AuthenticationException):
    def __init__(self):
        super().__init__(detail="Потрібна двофакторна аутентифікація")


class RateLimitException(BaseAppException):
    def __init__(self, retry_after: Optional[int] = None):
        detail = "Занадто багато запитів. Спробуйте пізніше"
        headers = None
        if retry_after:
            detail = f"Занадто багато запитів. Спробуйте через {retry_after} секунд"
            headers = {"Retry-After": str(retry_after)}

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers
        )