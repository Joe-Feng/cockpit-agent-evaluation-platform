import os

import httpx


def main() -> None:
    base_url = os.getenv("SMOKE_BASE_URL", "http://127.0.0.1:8000")
    with httpx.Client(base_url=base_url, timeout=5.0) as client:
        print(client.get("/health").json())
        print(client.get("/api/v1/dashboard/targets/cockpit_agents").json())
        print(client.get("/api/v1/alerts/events").json())


if __name__ == "__main__":
    main()
