"""Reproduce Unicode observations for the PY-BLT-020 experiment."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata


@dataclass(frozen=True)
class UnicodeProbe:
    """Stable public observations collected by the experiment."""

    composed: str
    decomposed: str
    composed_points: tuple[str, ...]
    decomposed_points: tuple[str, ...]
    exact_equal: bool
    nfc_equal: bool
    lower_equal: bool
    casefold_equal: bool
    india_flag: str
    india_flag_points: tuple[str, ...]
    family: str
    family_points: tuple[str, ...]
    unicode_database: str


def code_points(text: str) -> tuple[str, ...]:
    """Return the code-point sequence in stable U+XXXX notation."""
    return tuple(f"U+{ord(character):04X}" for character in text)


def run_experiment() -> UnicodeProbe:
    """Collect observations without depending on terminal glyph width."""
    composed = "\u00e9"
    decomposed = "e\u0301"
    sharp_s = "Stra\u00dfe"
    ascii_upper = "STRASSE"
    india_flag = "\U0001f1ee\U0001f1f3"
    family = "\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466"

    return UnicodeProbe(
        composed=composed,
        decomposed=decomposed,
        composed_points=code_points(composed),
        decomposed_points=code_points(decomposed),
        exact_equal=composed == decomposed,
        nfc_equal=unicodedata.normalize("NFC", composed)
        == unicodedata.normalize("NFC", decomposed),
        lower_equal=sharp_s.lower() == ascii_upper.lower(),
        casefold_equal=sharp_s.casefold() == ascii_upper.casefold(),
        india_flag=india_flag,
        india_flag_points=code_points(india_flag),
        family=family,
        family_points=code_points(family),
        unicode_database=unicodedata.unidata_version,
    )


def format_report(probe: UnicodeProbe) -> str:
    """Render a compact report suitable for captured experiment evidence."""
    return "\n".join(
        (
            f"visuals: composed={probe.composed!r}; decomposed={probe.decomposed!r}",
            "code-points: "
            f"composed={' '.join(probe.composed_points)}; "
            f"decomposed={' '.join(probe.decomposed_points)}",
            f"lengths: composed={len(probe.composed)}; decomposed={len(probe.decomposed)}",
            f"comparison: exact={probe.exact_equal}; NFC={probe.nfc_equal}",
            f"caseless: lower={probe.lower_equal}; casefold={probe.casefold_equal}",
            f"flag: len={len(probe.india_flag)}; points={' '.join(probe.india_flag_points)}",
            f"family: len={len(probe.family)}; points={' '.join(probe.family_points)}",
            "utf-8: "
            f"composed-bytes={len(probe.composed.encode('utf-8'))}; "
            f"family-bytes={len(probe.family.encode('utf-8'))}",
            f"Unicode database: {probe.unicode_database}",
        )
    )


def main() -> None:
    """Run the experiment and print only deterministic public observations."""
    print(format_report(run_experiment()))


if __name__ == "__main__":
    main()
