import httpx


class NotifierWorker:
    def __init__(self, webhook_url: str | None = None, client: httpx.Client | None = None) -> None:
        self.webhook_url = webhook_url
        self.client = client or httpx.Client()

    def deliver_once(self, event: dict) -> dict:
        if not self.webhook_url:
            return {
                "status": "skipped",
                "reason": "missing_webhook_url",
                "event": event,
            }

        response = self.client.post(self.webhook_url, json=event)
        response.raise_for_status()
        return {"status": "sent", "event": event}


def main() -> None:
    raise SystemExit("Use a process manager to launch the notifier worker")
