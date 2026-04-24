class BaseDomainException(Exception):
    """Base class for all domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
