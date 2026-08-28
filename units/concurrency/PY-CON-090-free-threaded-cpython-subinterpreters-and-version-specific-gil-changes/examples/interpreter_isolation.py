"""Demonstrate Python 3.14 subinterpreter namespace isolation."""

from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass


class InterpreterFeatureUnavailable(RuntimeError):
    """Raised when the Python 3.14 public interpreter API is unavailable."""


@dataclass(frozen=True)
class InterpreterObservation:
    """One subinterpreter's isolated state returned by message passing."""

    interpreter_id: int
    process_id: int
    state: tuple[str, ...]


@dataclass(frozen=True)
class IsolationReport:
    """State observed from two interpreters in the current process."""

    main_process_id: int
    observations: tuple[InterpreterObservation, ...]

    @property
    def interpreter_ids_are_distinct(self) -> bool:
        return len({item.interpreter_id for item in self.observations}) == len(
            self.observations
        )

    @property
    def all_share_main_process(self) -> bool:
        return all(
            item.process_id == self.main_process_id
            for item in self.observations
        )


def run_demo() -> IsolationReport:
    """Create two interpreters, mutate separate globals, and copy results out."""
    try:
        from concurrent import interpreters
    except ImportError as error:  # Python 3.11 compatibility path
        raise InterpreterFeatureUnavailable(
            "concurrent.interpreters requires Python 3.14+"
        ) from error

    output = interpreters.create_queue()
    workers = (interpreters.create(), interpreters.create())
    labels = (("alpha", "first-only"), ("beta", "second-only"))

    try:
        for worker, (label, private_value) in zip(workers, labels):
            worker.prepare_main(
                output=output,
                label=label,
                private_value=private_value,
            )
            worker.exec(
                textwrap.dedent(
                    """\
                    import os
                    from concurrent import interpreters

                    state = [label]
                    state.append(private_value)
                    output.put(
                        (
                            int(interpreters.get_current().id),
                            os.getpid(),
                            tuple(state),
                        )
                    )
                    """
                )
            )

        observations = tuple(
            InterpreterObservation(
                interpreter_id=interpreter_id,
                process_id=process_id,
                state=state,
            )
            for interpreter_id, process_id, state in (
                output.get(),
                output.get(),
            )
        )
    finally:
        for worker in reversed(workers):
            worker.close()

    return IsolationReport(
        main_process_id=os.getpid(),
        observations=observations,
    )


def main() -> None:
    """Print stable properties rather than environment-specific IDs."""
    report = run_demo()
    print(
        "subinterpreter IDs distinct: "
        f"{report.interpreter_ids_are_distinct}"
    )
    print(
        "subinterpreters share main PID: "
        f"{report.all_share_main_process}"
    )
    print(
        "isolated states: "
        f"{tuple(item.state for item in report.observations)}"
    )


if __name__ == "__main__":
    main()
