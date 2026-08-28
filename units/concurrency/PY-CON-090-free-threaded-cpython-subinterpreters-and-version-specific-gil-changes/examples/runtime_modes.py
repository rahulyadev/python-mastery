"""Inspect CPython concurrency capabilities without guessing from the version."""

from __future__ import annotations

import concurrent.futures
import importlib.util
import platform
import sys
import sysconfig
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeCapabilities:
    """Build, runtime, and interpreter-topology capabilities."""

    implementation: str
    python_version: str
    abi_flags: str
    free_threaded_build: bool
    gil_enabled: bool | None
    isolated_interpreters_supported: bool
    interpreters_module_available: bool
    interpreter_pool_available: bool

    @property
    def mode(self) -> str:
        """Return a deliberately conservative description of this runtime."""
        if self.implementation != "cpython":
            return "non-CPython runtime; CPython GIL probes are not authoritative"
        if not self.free_threaded_build:
            if self.gil_enabled is False:
                return "regular CPython build with an inconsistent GIL probe"
            if self.gil_enabled is None:
                return "regular CPython build; live GIL probe unavailable"
            return "regular CPython build with the GIL enabled"
        if self.gil_enabled is False:
            return "free-threaded CPython build with the GIL disabled"
        if self.gil_enabled is True:
            return "free-threaded CPython build with the GIL enabled"
        return "free-threaded CPython build with unknown runtime GIL state"


def detect_runtime_capabilities() -> RuntimeCapabilities:
    """Detect facts that must remain distinct during a migration."""
    gil_probe = getattr(sys, "_is_gil_enabled", None)
    gil_enabled = bool(gil_probe()) if callable(gil_probe) else None
    implementation = sys.implementation

    return RuntimeCapabilities(
        implementation=implementation.name,
        python_version=platform.python_version(),
        abi_flags=getattr(sys, "abiflags", ""),
        free_threaded_build=(
            sysconfig.get_config_var("Py_GIL_DISABLED") == 1
        ),
        gil_enabled=gil_enabled,
        isolated_interpreters_supported=bool(
            getattr(
                implementation,
                "supports_isolated_interpreters",
                False,
            )
        ),
        interpreters_module_available=(
            importlib.util.find_spec("concurrent.interpreters") is not None
        ),
        interpreter_pool_available=hasattr(
            concurrent.futures,
            "InterpreterPoolExecutor",
        ),
    )


def format_capabilities(report: RuntimeCapabilities) -> tuple[str, ...]:
    """Create stable, reviewable lines for logs and experiment output."""
    return (
        f"implementation: {report.implementation}",
        f"python: {report.python_version}",
        f"ABI flags: {report.abi_flags or '(none)'}",
        f"free-threaded build: {report.free_threaded_build}",
        f"GIL enabled: {report.gil_enabled}",
        (
            "isolated interpreters supported: "
            f"{report.isolated_interpreters_supported}"
        ),
        (
            "concurrent.interpreters available: "
            f"{report.interpreters_module_available}"
        ),
        (
            "InterpreterPoolExecutor available: "
            f"{report.interpreter_pool_available}"
        ),
        f"mode: {report.mode}",
    )


def main() -> None:
    """Print the current process's capabilities."""
    for line in format_capabilities(detect_runtime_capabilities()):
        print(line)


if __name__ == "__main__":
    main()
