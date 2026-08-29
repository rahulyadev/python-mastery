"""Unicode-aware string models for PY-BLT-020."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata


VALID_NORMAL_FORMS = frozenset({"NFC", "NFD", "NFKC", "NFKD"})


@dataclass(frozen=True)
class CodePointInfo:
    """Public Unicode information for one code point in a string."""

    index: int
    character: str
    notation: str
    name: str
    category: str
    combining_class: int


def inspect_code_points(text: str) -> tuple[CodePointInfo, ...]:
    """Describe each Unicode code point addressed by Python string indexing."""
    if not isinstance(text, str):
        raise TypeError("text must be str")

    return tuple(
        CodePointInfo(
            index=index,
            character=character,
            notation=f"U+{ord(character):04X}",
            name=unicodedata.name(character, "<unnamed>"),
            category=unicodedata.category(character),
            combining_class=unicodedata.combining(character),
        )
        for index, character in enumerate(text)
    )


def normalize_text(text: str, *, form: str = "NFC") -> str:
    """Return a documented Unicode normalization form after validating policy."""
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if form not in VALID_NORMAL_FORMS:
        choices = ", ".join(sorted(VALID_NORMAL_FORMS))
        raise ValueError(f"form must be one of: {choices}")
    return unicodedata.normalize(form, text)


def comparison_key(
    text: str,
    *,
    form: str = "NFC",
    caseless: bool = False,
) -> str:
    """Create an explicit comparison key without changing the display string."""
    normalized = normalize_text(text, form=form)
    if not caseless:
        return normalized

    # Case folding can itself change the code-point sequence. Re-normalizing keeps
    # the returned key in the requested normal form.
    return normalize_text(normalized.casefold(), form=form)


def equal_under_policy(
    left: str,
    right: str,
    *,
    form: str = "NFC",
    caseless: bool = False,
) -> bool:
    """Compare two strings under a named normalization and case policy."""
    return comparison_key(left, form=form, caseless=caseless) == comparison_key(
        right,
        form=form,
        caseless=caseless,
    )


def code_point_notation(text: str) -> tuple[str, ...]:
    """Return stable U+XXXX notation for every indexed string element."""
    return tuple(item.notation for item in inspect_code_points(text))


def main() -> None:
    """Print representative, deterministic Unicode observations."""
    composed = "caf\u00e9"
    decomposed = "cafe\u0301"
    family = "\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466"

    print(f"composed: len={len(composed)}; points={code_point_notation(composed)!r}")
    print(f"decomposed: len={len(decomposed)}; points={code_point_notation(decomposed)!r}")
    print(f"exact equality: {composed == decomposed}")
    print(f"NFC equality: {equal_under_policy(composed, decomposed)}")
    print(
        "caseless equality: "
        f"{equal_under_policy('Stra\u00dfe', 'STRASSE', caseless=True)}"
    )
    print(f"family: len={len(family)}; points={code_point_notation(family)!r}")


if __name__ == "__main__":
    main()
