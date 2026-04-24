import logging

from app.ports.output.email_port import IEmailPort, NotificationResult

_log = logging.getLogger(__name__)


class FakeEmailAdapter(IEmailPort):
    def send_invitation_sync(
        self, to_email: str, task_title: str, assigned_by: str
    ) -> NotificationResult:
        print(  # noqa: T201
            f"[FAKE EMAIL] To: {to_email} | Task: '{task_title}' | "
            f"Assigned by: {assigned_by}"
        )
        return NotificationResult(
            to=to_email,
            subject=f"You have been assigned to '{task_title}'",
            status="sent",
        )

    def send_invitation_async(
        self, to_email: str, task_title: str, assigned_by: str
    ) -> None:
        _log.info(
            "[FAKE EMAIL - ASYNC] To: %s | Task: '%s' | Assigned by: %s",
            to_email,
            task_title,
            assigned_by,
        )
