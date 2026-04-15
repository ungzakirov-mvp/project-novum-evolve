from fastapi import HTTPException, status


class ServiceDeskException(Exception):
    """Базовое исключение для Service Desk"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(ServiceDeskException):
    """Пользователь не найден"""
    pass


class UserAlreadyExistsException(ServiceDeskException):
    """Пользователь с таким email уже существует"""
    pass


class InvalidCredentialsException(ServiceDeskException):
    """Неверные учетные данные"""
    pass


class TicketNotFoundException(ServiceDeskException):
    """Тикет не найден"""
    pass


class UnauthorizedException(ServiceDeskException):
    """Недостаточно прав для выполнения операции"""
    pass


class ValidationException(ServiceDeskException):
    """Ошибка валидации данных"""
    pass


# HTTP Exception helpers
def user_not_found():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Пользователь не найден"
    )


def user_already_exists():
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Пользователь с таким email уже существует"
    )


def invalid_credentials():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный email или пароль",
        headers={"WWW-Authenticate": "Bearer"}
    )


def ticket_not_found():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Тикет не найден"
    )


def unauthorized():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав для выполнения этой операции"
    )
