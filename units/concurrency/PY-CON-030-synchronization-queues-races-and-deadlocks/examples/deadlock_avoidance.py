"""Avoid opposing-transfer deadlock with one global account-lock order."""

from __future__ import annotations

from dataclasses import dataclass, field
from queue import Queue
from threading import Barrier, Lock, Thread


@dataclass(slots=True)
class Account:
    account_id: str
    balance: int
    lock: Lock = field(default_factory=Lock, init=False, repr=False)


@dataclass(frozen=True, slots=True)
class TransferOutcome:
    label: str
    accepted: bool


def transfer(source: Account, target: Account, amount: int) -> bool:
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if source is target:
        return True

    first, second = sorted(
        (source, target),
        key=lambda account: account.account_id,
    )
    with first.lock:
        with second.lock:
            if source.balance < amount:
                return False
            source.balance -= amount
            target.balance += amount
            return True


def run_demo() -> tuple[Account, Account, list[TransferOutcome], bool]:
    alpha = Account("A", 100)
    beta = Account("B", 100)
    start_gate = Barrier(3, timeout=2.0)
    outcomes: Queue[TransferOutcome] = Queue()
    failures: Queue[BaseException] = Queue()

    def execute(label: str, source: Account, target: Account) -> None:
        try:
            start_gate.wait()
            outcomes.put(
                TransferOutcome(
                    label=label,
                    accepted=transfer(source, target, 10),
                )
            )
        except BaseException as exc:
            failures.put(exc)

    workers = [
        Thread(name="A-to-B", target=execute, args=("A-to-B", alpha, beta)),
        Thread(name="B-to-A", target=execute, args=("B-to-A", beta, alpha)),
    ]
    for worker in workers:
        worker.start()

    start_gate.wait()
    for worker in workers:
        worker.join(timeout=2.0)
    workers_alive = any(worker.is_alive() for worker in workers)
    if workers_alive:
        raise RuntimeError("opposing transfers did not terminate")
    if not failures.empty():
        raise failures.get_nowait()

    records = sorted(
        (outcomes.get_nowait() for _ in workers),
        key=lambda outcome: outcome.label,
    )
    assert alpha.balance + beta.balance == 200
    return alpha, beta, records, workers_alive


def main() -> None:
    alpha, beta, records, workers_alive = run_demo()
    print(f"accepted={sum(record.accepted for record in records)}")
    print(f"balances=A:{alpha.balance},B:{beta.balance}")
    print(f"total={alpha.balance + beta.balance}")
    print(f"workers_alive={workers_alive}")


if __name__ == "__main__":
    main()
