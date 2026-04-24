from app.domain.exceptions.base import BaseDomainException


class TaskListNotFoundException(BaseDomainException):
    pass


class TaskListAlreadyExistsException(BaseDomainException):
    pass
