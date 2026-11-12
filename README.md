# Week 6 — AI Code Review & Testing

A FastAPI + SQLite Habit Tracker with two completed features: request input
validation and a seven-day check-in summary. This repository is the integrated
submission for the Week 6 AI code review and testing assignment.

## Features and endpoints

| Feature | Behavior | Endpoint |
|---|---|---|
| Input validation | Rejects blank habit names and malformed or impossible dates; non-string JSON values are covered by tests. | `POST /habits` and `POST /habits/{habit_id}/checkin` |
| Weekly summary | Counts check-ins within the seven-day window ending today, inclusive; ignores malformed legacy dates. | `GET /habits/{habit_id}/summary` |

Other API endpoints: `GET /habits`, `GET /habits/{habit_id}/checkins`.

## Development and retrospective review PRs

| Feature | Original development PR | Retrospective CodeRabbit review PR |
|---|---|---|
| Input Validation | [PR #1](https://github.com/betulyildizs/week6-habit-tracker/pull/1) | [PR #5](https://github.com/betulyildizs/week6-habit-tracker/pull/5) |
| Weekly Summary | [PR #2](https://github.com/betulyildizs/week6-habit-tracker/pull/2) | [PR #6](https://github.com/betulyildizs/week6-habit-tracker/pull/6) |

PRs #5 and #6 are review-only retrospective assessments. They reproduce the
historical feature diffs for CodeRabbit review; they are not implementation PRs
and must not be merged.

## Assignment evidence

- [Write-up and review/test evidence](writeup.md)
- [Feature task descriptions](docs/TASKS.md)
- [GitHub Actions quality-gate workflow](.github/workflows/quality.yml)

## Setup and run

From the repository root, create and activate a virtual environment, then
install the application and test dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the API and browse the interactive documentation at `http://localhost:8000/docs`:

```powershell
python -m uvicorn main:app --reload
```

## Tests and quality gates

Run the test suite:

```powershell
python -m pytest -q
```

Run the repository's complete local quality-gate script (Black, Ruff, and
Pytest):

```powershell
.\check.ps1
```

The equivalent individual checks are:

```powershell
python -m black --check .
python -m ruff check .
python -m pytest -q
```

GitHub Actions runs the same three checks on pushes and pull requests using
Python 3.13.

## Rubric evidence checklist

- [x] Two implemented features with documented endpoints and separate original PRs.
- [x] Feature behavior and edge cases covered by automated tests.
- [x] Manual inspection and Copilot review findings distinguished in the [write-up](writeup.md).
- [x] Malformed legacy-date regression reproduced, fixed, and documented.
- [x] Retrospective CodeRabbit assessments and their scope documented in the [write-up](writeup.md).
- [x] Local quality gates and integrated GitHub Actions results recorded in the [write-up](writeup.md).
