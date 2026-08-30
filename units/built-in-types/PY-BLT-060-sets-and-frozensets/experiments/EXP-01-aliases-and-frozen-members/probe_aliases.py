"""Observe container membership separately from member-object state."""


class Job:
    """Identity-based equality and hashing; status is not a key field."""

    def __init__(self, status: str) -> None:
        self.status = status


def main() -> None:
    source = {"api"}
    alias = source
    copied = source.copy()
    frozen = frozenset(source)
    source.add("worker")
    print(f"after add: source={sorted(source)}, alias={sorted(alias)}")
    print(f"snapshots: copied={sorted(copied)}, frozen={sorted(frozen)}")
    print(f"source is alias: {source is alias}")

    source = source | {"cron"}
    print(f"after rebind: source={sorted(source)}, alias={sorted(alias)}")
    print(f"source is alias: {source is alias}")

    previous_frozen = frozen
    frozen |= {"batch"}
    print(f"frozen |=: current={sorted(frozen)}, previous={sorted(previous_frozen)}")
    print(f"same frozen object: {frozen is previous_frozen}")

    job = Job("queued")
    jobs = frozenset([job])
    job.status = "done"
    print(f"member status: {next(iter(jobs)).status}")
    print(f"member still present: {job in jobs}")


if __name__ == "__main__":
    main()
