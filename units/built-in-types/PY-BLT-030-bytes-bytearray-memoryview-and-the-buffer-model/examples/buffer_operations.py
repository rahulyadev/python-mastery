"""Buffer metadata and fixed-size mutation examples for PY-BLT-030."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BufferInfo:
    """A durable snapshot of public memoryview metadata."""

    format: str
    itemsize: int
    ndim: int
    shape: tuple[int, ...]
    strides: tuple[int, ...]
    nbytes: int
    readonly: bool
    c_contiguous: bool


def _acquire_view(buffer: object) -> memoryview:
    """Acquire a memoryview with an API-focused error message."""
    try:
        return memoryview(buffer)
    except TypeError:
        raise TypeError("buffer must support the buffer protocol") from None


def describe_buffer(buffer: object) -> BufferInfo:
    """Return public layout and mutability metadata without retaining a view."""
    view = _acquire_view(buffer)
    try:
        return BufferInfo(
            format=view.format,
            itemsize=view.itemsize,
            ndim=view.ndim,
            shape=view.shape,
            strides=view.strides,
            nbytes=view.nbytes,
            readonly=view.readonly,
            c_contiguous=view.c_contiguous,
        )
    finally:
        view.release()


def checksum_octets(buffer: object) -> int:
    """Return a simple modulo-256 checksum over one contiguous byte view."""
    view = _acquire_view(buffer)
    try:
        if not view.c_contiguous:
            raise ValueError("buffer must be C-contiguous")

        octets = view.cast("B")
        try:
            return sum(octets) % 256
        finally:
            octets.release()
    finally:
        view.release()


def overwrite_window(buffer: object, start: int, replacement: bytes) -> None:
    """Overwrite an equal-size byte window without resizing the exporter."""
    if type(start) is not int:
        raise TypeError("start must be a plain integer")
    if not isinstance(replacement, bytes):
        raise TypeError("replacement must be bytes")

    view = _acquire_view(buffer)
    try:
        if view.readonly:
            raise TypeError("buffer must be writable")
        if not view.c_contiguous:
            raise ValueError("buffer must be C-contiguous")

        octets = view.cast("B")
        try:
            stop = start + len(replacement)
            if start < 0 or stop > octets.nbytes:
                raise ValueError("replacement window is out of bounds")
            octets[start:stop] = replacement
        finally:
            octets.release()
    finally:
        view.release()


def main() -> None:
    """Show a copied slice beside an aliasing view and fixed-size mutation."""
    data = bytearray(b"HEADsecretTAIL")
    copied = data[4:10]
    view = memoryview(data)[4:10]
    try:
        view[0] = ord("S")
        print(f"after-view-write: exporter={data!r}; copy={copied!r}")
    finally:
        view.release()

    overwrite_window(data, 4, b"******")
    print(f"after-overwrite: exporter={data!r}; checksum={checksum_octets(data)}")
    print(f"metadata: {describe_buffer(data)!r}")


if __name__ == "__main__":
    main()
