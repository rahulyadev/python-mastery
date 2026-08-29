"""Strict text/binary boundary and framed-protocol examples for PY-BLT-030."""

from __future__ import annotations

from dataclasses import dataclass
import struct


PROTOCOL_VERSION = 1
MAX_PAYLOAD_BYTES = (1 << 16) - 1
HEADER = struct.Struct("!BH")


class FrameError(ValueError):
    """Raised when bytes do not satisfy the example frame contract."""


@dataclass(frozen=True)
class TextFrame:
    """A decoded frame with its binary-boundary facts kept explicit."""

    version: int
    text: str
    payload_size: int


def encode_text_frame(text: str) -> bytes:
    """Encode one UTF-8 text payload behind a version and byte-length header."""
    if not isinstance(text, str):
        raise TypeError("text must be str")

    payload = text.encode("utf-8", errors="strict")
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise FrameError(f"payload exceeds {MAX_PAYLOAD_BYTES} bytes")

    return HEADER.pack(PROTOCOL_VERSION, len(payload)) + payload


def _acquire_view(data: object) -> memoryview:
    """Acquire a view while replacing an implementation-shaped TypeError."""
    try:
        return memoryview(data)
    except TypeError:
        raise TypeError("data must support the buffer protocol") from None


def decode_text_frame(data: object) -> TextFrame:
    """Validate and decode one complete, C-contiguous example frame.

    The header is inspected through a view. Creating the returned ``str`` is an
    intentional text-boundary conversion and therefore necessarily creates a
    text object from the payload bytes.
    """
    view = _acquire_view(data)
    try:
        if not view.c_contiguous:
            raise FrameError("frame must be C-contiguous")

        octets = view.cast("B")
        try:
            if octets.nbytes < HEADER.size:
                raise FrameError("frame is shorter than its header")

            version, declared_size = HEADER.unpack_from(octets, 0)
            actual_size = octets.nbytes - HEADER.size

            if version != PROTOCOL_VERSION:
                raise FrameError(f"unsupported protocol version: {version}")
            if actual_size != declared_size:
                raise FrameError(
                    "payload length mismatch: "
                    f"declared {declared_size}, received {actual_size}"
                )

            payload = octets[HEADER.size :]
            try:
                try:
                    text = payload.tobytes().decode("utf-8", errors="strict")
                except UnicodeDecodeError as exc:
                    raise FrameError("payload is not valid UTF-8") from exc
            finally:
                payload.release()
        finally:
            octets.release()
    finally:
        view.release()

    return TextFrame(
        version=version,
        text=text,
        payload_size=declared_size,
    )


def main() -> None:
    """Print a deterministic round trip whose text and byte lengths differ."""
    text = "A\u00e9"
    encoded = encode_text_frame(text)
    decoded = decode_text_frame(encoded)

    print(f"text: value={text!r}; code-points={len(text)}")
    print(f"frame: hex={encoded.hex()}; bytes={len(encoded)}")
    print(f"decoded: {decoded!r}")


if __name__ == "__main__":
    main()
