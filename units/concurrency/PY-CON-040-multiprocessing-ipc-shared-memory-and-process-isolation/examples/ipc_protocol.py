"""Use a byte-oriented Pipe protocol instead of automatic pickle deserialization."""

from __future__ import annotations

import json
import multiprocessing as mp
from multiprocessing.connection import Connection
from typing import Any


def decode_request(payload: bytes) -> dict[str, Any]:
    """Validate a deliberately small JSON request schema."""

    decoded = json.loads(payload.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("request must be an object")
    if set(decoded) != {"operation", "values"}:
        raise ValueError("request fields must be operation and values")
    if decoded["operation"] != "sum_squares":
        raise ValueError("unsupported operation")
    values = decoded["values"]
    if (
        not isinstance(values, list)
        or len(values) > 100
        or any(type(value) is not int for value in values)
    ):
        raise ValueError("values must be a list of at most 100 integers")
    return decoded


def serve_once(connection: Connection) -> None:
    """Handle one request and always return a schema-controlled response."""

    try:
        request = decode_request(connection.recv_bytes(maxlength=4096))
        result = sum(value * value for value in request["values"])
        response: dict[str, Any] = {"ok": True, "result": result}
    except Exception as error:
        response = {"ok": False, "error": f"{type(error).__name__}: {error}"}
    try:
        connection.send_bytes(json.dumps(response, sort_keys=True).encode("utf-8"))
    finally:
        connection.close()


def request_once(payload: dict[str, Any]) -> dict[str, Any]:
    """Send one request over a dedicated end of a duplex Pipe."""

    context = mp.get_context("spawn")
    parent_connection, child_connection = context.Pipe(duplex=True)
    process = context.Process(target=serve_once, args=(child_connection,), name="ipc-server")
    process.start()
    child_connection.close()
    try:
        parent_connection.send_bytes(json.dumps(payload).encode("utf-8"))
        if not parent_connection.poll(10):
            raise TimeoutError("IPC worker did not answer")
        response = json.loads(parent_connection.recv_bytes(maxlength=4096).decode("utf-8"))
        process.join(timeout=10)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            raise TimeoutError("IPC worker did not exit")
        if process.exitcode != 0:
            raise RuntimeError(f"IPC worker exited with code {process.exitcode}")
    finally:
        parent_connection.close()
        if not process.is_alive():
            process.close()
    return response


def run_demo() -> tuple[dict[str, Any], dict[str, Any]]:
    """Return one accepted and one rejected protocol response."""

    accepted = request_once({"operation": "sum_squares", "values": [2, 3, 4]})
    rejected = request_once({"operation": "sum_squares", "values": [1, "bad"]})
    return accepted, rejected


if __name__ == "__main__":
    for demo_response in run_demo():
        print(demo_response)
