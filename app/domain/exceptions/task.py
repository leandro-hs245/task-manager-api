from app.domain.exceptions.base import BaseDomainException


class TaskNotFoundException(BaseDomainException):
    pass


class TaskAlreadyExistsException(BaseDomainException):
    pass


class InvalidTaskStatusTransitionException(BaseDomainException):
    pass
