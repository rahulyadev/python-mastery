"""Demonstrate reusable logic and an explicit script entry point."""


def build_status(service: str) -> str:
    """Return a synthetic one-line status for a service."""
    normalized_service = service.strip() or "api"
    return f"{normalized_service}: ok"


def main() -> None:
    """Read a service name and print its synthetic status."""
    service = input("Service name: ")
    print(build_status(service))


if __name__ == "__main__":
    main()
