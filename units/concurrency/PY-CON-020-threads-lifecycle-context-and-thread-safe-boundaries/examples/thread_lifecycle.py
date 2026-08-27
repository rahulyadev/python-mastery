"""Show the observable lifecycle of one deliberately controlled thread."""

from __future__ import annotations

from dataclasses import dataclass
from queue import Queue
from threading import Event, Thread


@dataclass(frozen=True, slots=True)
class Outcome:
    """An immutable value transferred from the worker to its owner."""

    source: str
    value: str


def load_profile(
    user_id: str,
    *,
    started: Event,
    may_finish: Event,
    outcomes: Queue[Outcome],
) -> None:
    """Wait at a controlled point, then publish exactly one result."""

    started.set()
    may_finish.wait()
    outcomes.put(Outcome(source="profile-loader", value=f"profile-{user_id}"))


def main() -> None:
    started = Event()
    may_finish = Event()
    outcomes: Queue[Outcome] = Queue()
    worker = Thread(
        name="profile-loader",
        target=load_profile,
        kwargs={
            "user_id": "42",
            "started": started,
            "may_finish": may_finish,
            "outcomes": outcomes,
        },
        daemon=False,
    )

    print(f"new: alive={worker.is_alive()}, ident={worker.ident}")
    worker.start()

    if not started.wait(timeout=1.0):
        raise RuntimeError("worker did not reach its controlled waiting point")
    print(f"running: alive={worker.is_alive()}")

    may_finish.set()
    worker.join(timeout=1.0)
    if worker.is_alive():
        raise RuntimeError("worker did not terminate before the deadline")

    print(f"terminated: alive={worker.is_alive()}")
    outcome = outcomes.get_nowait()
    print(f"outcome: {outcome.source} -> {outcome.value}")


if __name__ == "__main__":
    main()
