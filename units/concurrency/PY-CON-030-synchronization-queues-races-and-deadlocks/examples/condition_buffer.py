"""Use a condition predicate to coordinate a one-slot teaching buffer."""

from __future__ import annotations

from queue import Queue
from threading import Condition, Thread
from typing import Generic, TypeVar, cast


T = TypeVar("T")
_EMPTY = object()


class EndOfStream(Exception):
    """Raised after the closed buffer has been fully drained."""


class OneSlotBuffer(Generic[T]):
    """A small condition example; production code should prefer queue.Queue."""

    def __init__(self) -> None:
        self._condition = Condition()
        self._item: object = _EMPTY
        self._closed = False

    def put(self, item: T) -> None:
        with self._condition:
            self._condition.wait_for(
                lambda: self._item is _EMPTY or self._closed
            )
            if self._closed:
                raise RuntimeError("buffer is closed")
            self._item = item
            self._condition.notify_all()

    def get(self) -> T:
        with self._condition:
            self._condition.wait_for(
                lambda: self._item is not _EMPTY or self._closed
            )
            if self._item is _EMPTY:
                raise EndOfStream
            item = cast(T, self._item)
            self._item = _EMPTY
            self._condition.notify_all()
            return item

    def close(self) -> None:
        with self._condition:
            self._closed = True
            self._condition.notify_all()

    @property
    def closed(self) -> bool:
        with self._condition:
            return self._closed


def run_demo() -> tuple[list[int], bool, bool]:
    buffer: OneSlotBuffer[int] = OneSlotBuffer()
    processed: list[int] = []
    failures: Queue[BaseException] = Queue()

    def produce() -> None:
        try:
            for value in (1, 2, 3):
                buffer.put(value)
        except BaseException as exc:
            failures.put(exc)
        finally:
            buffer.close()

    def consume() -> None:
        try:
            while True:
                processed.append(buffer.get() * 2)
        except EndOfStream:
            return
        except BaseException as exc:
            failures.put(exc)

    consumer = Thread(name="condition-consumer", target=consume)
    producer = Thread(name="condition-producer", target=produce)
    consumer.start()
    producer.start()
    producer.join(timeout=2.0)
    consumer.join(timeout=2.0)

    workers_alive = producer.is_alive() or consumer.is_alive()
    if workers_alive:
        raise RuntimeError("condition demonstration did not terminate")
    if not failures.empty():
        raise failures.get_nowait()

    assert processed == [2, 4, 6]
    return processed, buffer.closed, workers_alive


def main() -> None:
    processed, closed, workers_alive = run_demo()
    print(f"processed={processed}")
    print(f"buffer_closed={closed}")
    print(f"workers_alive={workers_alive}")


if __name__ == "__main__":
    main()
