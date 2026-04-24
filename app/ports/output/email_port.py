from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NotificationResult:
    to: str
    subject: str
    status: str


class IEmailPort(ABC):
    @abstractmethod
    def send_invitation_sync(
        self, to_email: str, task_title: str, assigned_by: str
    ) -> NotificationResult: ...

    @abstractmethod
    def send_invitation_async(
        self, to_email: str, task_title: str, assigned_by: str
    ) -> None: ...
