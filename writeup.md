# Week 6 — AI Code Review & Testing

## Scope and sources

This report covers the Input Validation and Weekly Summary feature branches,
their recorded implementation-time tests, and the project quality gates. The
repository contains `README.md`, `docs/TASKS.md`, `pyproject.toml`, and
`check.ps1`, but no separate original-assignment-instructions file. The feature
requirements below are therefore grounded in `docs/TASKS.md` and the assignment
details supplied for this work.

## Quality gates

`check.ps1` runs Black in check-only mode, Ruff, and Pytest, stopping with a
nonzero exit code when a gate fails. The equivalent local commands are:

```powershell
.\.venv\Scripts\python.exe -m black --check .
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
```

Run all three through the repository script with:

```powershell
.\check.ps1
```

Black and Ruff use the project's `pyproject.toml` settings: line length 88,
with Ruff selecting `E4`, `E7`, `E9`, and `F`. The GitHub Actions workflow
installs the application dependencies from `requirements.txt` plus Black and
Ruff, then runs the same three checks on pushes and pull requests using Python
3.13.

## PR #1 — Input Validation

[PR #1: Input Validation](https://github.com/betulyildizs/week6-habit-tracker/pull/1)
adds Pydantic validators to reject empty or whitespace-only habit names and
check-in dates that are not real dates in strict `YYYY-MM-DD` form. Valid
inputs retain the original response shapes. Tests cover blank names, malformed
and impossible dates, valid dates, and non-string JSON values (null, integer,
float, boolean, list, and object) for both fields.

The Copilot review found no confirmed defect and recommended adding explicit
non-string input coverage; those tests were subsequently added. In the
implementation session, Black and Ruff passed, and the expanded validation
suite passed with **24 tests**. The project configuration and inputs are
preserved as provided; nonblank names are not trimmed.

## PR #2 — Weekly Summary

[PR #2: Weekly Summary](https://github.com/betulyildizs/week6-habit-tracker/pull/2)
adds `GET /habits/{habit_id}/summary`. It counts check-in records from today
through the preceding six calendar days, inclusive, returns 404 for an unknown
habit, and counts duplicate records rather than distinct days. Its deterministic
tests freeze the date and cover zero records, both included boundaries, the day
just outside the window, future dates, duplicate records, and unknown habits.

The Copilot review identified that the initial SQL used lexical `BETWEEN` on
the text date column and could include malformed legacy values such as
`2026-09-16x`. A regression test was run before the fix:

```powershell
.\.venv\Scripts\python.exe -m pytest -q test_main.py -k "malformed_legacy or future_checkins"
```

Observed result: **1 failed, 1 passed**, with exit code **1**. The malformed
record was incorrectly counted (`1` instead of the expected `0`). The fix
retains the parameterized SQL date-range prefilter, parses each candidate with
`date.fromisoformat`, checks a canonical ISO round-trip and the actual date
bounds, and counts each eligible row. This excludes malformed legacy records
without changing duplicate-counting semantics or the response shape. After the
fix, Black and Ruff passed and Pytest passed with **10 tests**.

### Human and AI review comparison

Manual code inspection was performed before the independent Copilot reviews.
These were informal observations, not submitted GitHub reviews:

- **PR #1:** Valid, nonblank habit names retain leading and trailing
  whitespace. Trimming could be a normalization improvement, but it was not a
  requirement violation and no defect was recorded.
- **PR #2:** The summary counts duplicate same-day check-in records
  individually, consistent with the task's wording to count check-ins. The
  original implementation also relied on lexicographical ordering of ISO date
  strings for the SQL range comparison.

The Copilot review of **PR #1** found no confirmed defect and recommended tests
for non-string JSON values; those tests were added. For **PR #2**, Copilot
identified malformed legacy date strings that could inflate the summary. A
regression test reproduced the issue with a nonzero failing result, and the
implementation was fixed to exclude malformed dates. The GitHub API showed no
submitted review records or inline review comments for either PR; these
informal manual observations should not be mistaken for formal GitHub review
feedback. No CodeRabbit review is claimed.

## Tradeoffs and lessons learned

The weekly-summary fix validates candidate dates in Python after narrowing
rows in SQL. This keeps date parsing explicit and portable while accepting a
small amount of Python work for candidate rows; if the table grows
substantially, a canonical date constraint at write time and a migration or
indexing strategy may be appropriate. The tests insert a malformed legacy row
directly so they verify the route remains robust even when older data bypasses
current request validation.

**Reflection:** The review process showed why boundary-focused tests matter
even when the main implementation appears straightforward. Strict input
validation protects new data, but it does not repair or sanitize records
already stored. The failing regression test made that gap observable before
the fix was applied. Combining Copilot review with direct code inspection and
executable regressions gave stronger evidence than relying on a passing
happy-path suite alone.

## Verification notes

The branch implementation runs recorded above are the feature-specific results.
The new workflow has not yet run on GitHub in this change, and no GitHub Actions
result is claimed here.

On the current documentation branch, the direct quality-gate commands all
passed: Black reported two files unchanged, Ruff reported all checks passed,
and Pytest reported **3 passed** with one existing Starlette/httpx deprecation
warning. Direct execution of `.\check.ps1` was blocked by the local PowerShell
execution policy; its three commands were run individually instead.
