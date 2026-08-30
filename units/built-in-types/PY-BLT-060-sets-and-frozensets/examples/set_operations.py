"""Small, deterministic demonstrations for PY-BLT-060 (Python 3.11+)."""


def algebra() -> dict[str, list[str]]:
    """Present results in sorted order, without implying sets have an order."""
    current = {"api", "cache", "worker"}
    desired = {"cache", "cron"}
    return {
        "union": sorted(current | desired),
        "intersection": sorted(current & desired),
        "current_only": sorted(current - desired),
        "desired_only": sorted(desired - current),
        "symmetric_difference": sorted(current ^ desired),
    }


def mutation() -> dict[str, object]:
    services = {"api"}
    alias = services
    added = services.add("worker")
    updated = services.update(["cache", "worker"])
    services.discard("missing")
    return {
        "members": sorted(services),
        "same_object": alias is services,
        "add_return": added,
        "update_return": updated,
    }


def frozen_key() -> tuple[str, bool]:
    """An unordered group is a key; order and repeats have no meaning here."""
    plans = {frozenset(["json", "gzip"]): "compressed-json"}
    requested = frozenset(["gzip", "json", "json"])
    return plans[requested], requested == {"json", "gzip"}


def main() -> None:
    for name, members in algebra().items():
        print(f"{name}: {members}")
    print(f"mutation: {mutation()}")
    print(f"frozen key: {frozen_key()}")
    numeric_values = [1, True, 1.0]
    print(f"equal numeric members: {len(set(numeric_values))}")
    print(f"iterable method: {sorted({'api', 'cache'}.intersection(['cache']))}")


if __name__ == "__main__":
    main()
