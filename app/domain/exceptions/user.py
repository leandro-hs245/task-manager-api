from app.domain.exceptions.base import BaseDomainException


class UserNotFoundException(BaseDomainException):
    pass


class UserAlreadyExistsException(BaseDomainException):
    pass


class InvalidCredentialsException(BaseDomainException):
    pass
