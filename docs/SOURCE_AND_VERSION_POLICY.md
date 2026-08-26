# Source and Version Policy

[Back to README](../README.md) · [Workflow](WORKFLOW.md)

## Baseline

- Canonical feature baseline: **Python 3.14**.
- Initially verified runtime for this bootstrap: **CPython 3.14.7**.
- Verification date: **2026-08-26**.
- Interview-compatibility baseline: **Python 3.11**.
- Preview releases are non-canonical until stable.
- `.python-version` records the initially tested runtime.
- The first Codex setup must re-verify the latest stable CPython 3.14 maintenance release before changing the pin.

Official release references:

- [Python 3.14.7 release](https://www.python.org/downloads/release/python-3147/)
- [Python downloads](https://www.python.org/downloads/)

## Source order

Prefer:

1. [Python Language Reference](https://docs.python.org/3/reference/)
2. [Python Standard Library](https://docs.python.org/3/library/)
3. Accepted or final [Python Enhancement Proposals](https://peps.python.org/)
4. [Python Developer’s Guide](https://devguide.python.org/)
5. [CPython source](https://github.com/python/cpython) and official implementation notes
6. [Python/C API documentation](https://docs.python.org/3/c-api/)
7. Authoritative third-party tool documentation
8. Strong secondary explanations only when primary material is insufficient

The tutorial may help with intuition, but it does not override the Language Reference or a documented standard-library contract.

## Claim classification

Classify subtle claims as one of:

- Language guarantee
- Standard-library contract
- CPython implementation detail
- Tooling behaviour
- Platform-specific behaviour
- Version-dependent behaviour

Do not turn a CPython observation into a universal Python guarantee.

## Citation policy

Cite only sources actually opened and read.

Use nearby citations for important claims involving:

- language semantics;
- version changes;
- surprising edge cases;
- performance;
- security;
- concurrency;
- memory;
- CPython internals.

Do not add citations mechanically after every ordinary explanatory sentence.

Prefer original explanations over copied documentation. For subtle claims, identify the exact documentation section, PEP, or CPython file and relevant symbol. Keep each unit’s source section compact and limited to material actually used.

## Interview compatibility

For syntax or behaviour introduced after Python 3.11:

1. State the first supported Python version.
2. Label the Python 3.14 canonical form.
3. Provide a useful Python 3.11-compatible alternative when practical.
4. Explain whether the difference is syntax, public API, typing-only, tooling-only, or CPython-specific.
5. Do not assume an interview platform supports the newest feature.

Do not force an inferior legacy style when the modern recommendation is clearer. Show both when compatibility matters.

Example callouts:

> **Python 3.14 canonical form**
> Use the clearest current form supported by the canonical runtime.

> **First available in Python 3.12**
> State why this syntax or API cannot run unchanged on Python 3.11.

> **Python 3.11-compatible alternative**
> Show the practical equivalent and any semantic limitation.

> **CPython 3.14 implementation detail**
> Label the observation and avoid portability claims.

## CPython and alternative interpreters

The Language Reference and public-library contracts remain the portable authority.

Add portability notes when material depends on:

- reference counting;
- object layout;
- bytecode;
- finalization timing;
- the Global Interpreter Lock;
- just-in-time compilation;
- C extensions;
- CPython-specific atomicity or caching.

CPython bytecode is an implementation detail and may change between releases or interpreters. Exact opcode sequences must be version-labelled.

## Experiments

Every runtime experiment records:

- question;
- hypothesis;
- Python version;
- implementation;
- build type;
- operating system;
- architecture;
- relevant flags and dependencies;
- exact command;
- actual observed output;
- interpretation;
- limitations.

Never claim that an experiment ran when it did not.

## Benchmarks

Every benchmark records:

- workload and input distribution;
- environment;
- warm-up policy;
- trial count;
- timing method;
- raw or summarized observations;
- uncertainty and limitations.

Distinguish asymptotic reasoning from measured timing.

Do not generalize one machine-specific observation into a universal claim. Never invent a speedup, memory reduction, benchmark result, profiler finding, or experiment outcome.

## Security claims

Use authoritative sources for:

- unsafe deserialization;
- subprocess and shell boundaries;
- temporary-file behaviour;
- path handling;
- cryptographic primitives;
- random versus secure random;
- dependency and supply-chain guidance;
- concurrency or resource-exhaustion risks.

Do not improvise security guarantees from intuition.

## Limited API and Stable ABI

In CPython extension material, distinguish:

- the full C API;
- the Limited API;
- the Stable ABI;
- implementation-specific macros;
- version-specific binary compatibility;
- free-threaded extension compatibility.

Do not use these terms interchangeably.

## Release-upgrade process

When a new stable feature release is considered:

1. Verify it through official Python sources.
2. Update the baseline and verification date.
3. Update `.python-version`.
4. Synchronize the environment and lock file.
5. Run repository validation and all existing tests.
6. Audit version-sensitive units.
7. Add version overlays instead of rewriting historical behaviour.
8. Prioritize typing, `asyncio`, bytecode, GIL/free-threading, packaging, deprecations, and removed APIs.
9. Record unresolved portability questions.
10. Do not mass-rewrite approved notes without need.
