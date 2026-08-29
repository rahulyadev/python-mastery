"""Reproduce aliasing, layout metadata, and view lifetime for PY-BLT-030."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProbeResult:
    """Deterministic public observations from the buffer experiment."""

    initial_exporter: str
    copied_slice: str
    initial_view: str
    exporter_after_view_write: str
    copy_after_view_write: str
    view_after_view_write: str
    exporter_after_direct_write: str
    view_after_direct_write: str
    readonly_after_direct_write: str
    view_metadata: str
    resize_while_exported: str
    access_after_release: str
    resized_length: int
    resized_tail: int
    matrix_metadata: str
    matrix_element: int
    strided_bytes: str
    strided_metadata: str


def run_experiment() -> ProbeResult:
    """Run the bounded experiment using only public buffer operations."""
    exporter = bytearray(range(8))
    copied = exporter[2:6]
    view = memoryview(exporter)[2:6]
    readonly = view.toreadonly()

    initial_exporter = exporter.hex()
    copied_slice = copied.hex()
    initial_view = view.hex()

    view[0] = 0xAA
    exporter_after_view_write = exporter.hex()
    copy_after_view_write = copied.hex()
    view_after_view_write = view.hex()

    exporter[3] = 0xBB
    exporter_after_direct_write = exporter.hex()
    view_after_direct_write = view.hex()
    readonly_after_direct_write = readonly.hex()
    view_metadata = (
        f"format={view.format}; itemsize={view.itemsize}; ndim={view.ndim}; "
        f"shape={view.shape}; strides={view.strides}; nbytes={view.nbytes}; "
        f"readonly={view.readonly}; c_contiguous={view.c_contiguous}"
    )

    try:
        exporter.append(0xFF)
    except BufferError as exc:
        resize_while_exported = type(exc).__name__
    else:  # pragma: no cover - a failed invariant must stop the experiment
        raise AssertionError("resizing unexpectedly succeeded while views existed")

    readonly.release()
    view.release()

    try:
        view[0]
    except ValueError as exc:
        access_after_release = type(exc).__name__
    else:  # pragma: no cover - a failed invariant must stop the experiment
        raise AssertionError("released view unexpectedly remained usable")

    exporter.append(0xFF)

    raw = bytes(range(8))
    root = memoryview(raw)
    matrix = root.cast("B", shape=[2, 4])
    strided = root[::2]
    try:
        matrix_metadata = (
            f"format={matrix.format}; itemsize={matrix.itemsize}; "
            f"ndim={matrix.ndim}; shape={matrix.shape}; "
            f"strides={matrix.strides}; nbytes={matrix.nbytes}"
        )
        matrix_element = matrix[1, 2]
        strided_bytes = strided.hex()
        strided_metadata = (
            f"shape={strided.shape}; strides={strided.strides}; "
            f"c_contiguous={strided.c_contiguous}"
        )
    finally:
        strided.release()
        matrix.release()
        root.release()

    return ProbeResult(
        initial_exporter=initial_exporter,
        copied_slice=copied_slice,
        initial_view=initial_view,
        exporter_after_view_write=exporter_after_view_write,
        copy_after_view_write=copy_after_view_write,
        view_after_view_write=view_after_view_write,
        exporter_after_direct_write=exporter_after_direct_write,
        view_after_direct_write=view_after_direct_write,
        readonly_after_direct_write=readonly_after_direct_write,
        view_metadata=view_metadata,
        resize_while_exported=resize_while_exported,
        access_after_release=access_after_release,
        resized_length=len(exporter),
        resized_tail=exporter[-1],
        matrix_metadata=matrix_metadata,
        matrix_element=matrix_element,
        strided_bytes=strided_bytes,
        strided_metadata=strided_metadata,
    )


def format_report(result: ProbeResult) -> str:
    """Format exact observations without addresses or platform-sensitive reprs."""
    return "\n".join(
        (
            "initial: "
            f"exporter={result.initial_exporter}; copy={result.copied_slice}; "
            f"view={result.initial_view}",
            "view-write: "
            f"exporter={result.exporter_after_view_write}; "
            f"copy={result.copy_after_view_write}; view={result.view_after_view_write}",
            "exporter-write: "
            f"exporter={result.exporter_after_direct_write}; "
            f"view={result.view_after_direct_write}; "
            f"readonly-view={result.readonly_after_direct_write}",
            f"view-metadata: {result.view_metadata}",
            f"resize-while-exported: {result.resize_while_exported}",
            f"access-after-release: {result.access_after_release}",
            "resize-after-release: "
            f"length={result.resized_length}; tail={result.resized_tail}",
            "matrix: "
            f"{result.matrix_metadata}; element[1,2]={result.matrix_element}",
            "strided: "
            f"bytes={result.strided_bytes}; {result.strided_metadata}",
        )
    )


def main() -> None:
    """Print the complete deterministic report."""
    print(format_report(run_experiment()))


if __name__ == "__main__":
    main()
