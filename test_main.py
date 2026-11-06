from datetime import date as real_date

from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


class FrozenDate(real_date):
    @classmethod
    def today(cls):
        return cls(2026, 9, 22)


def test_create_and_list_habit():
    r = client.post("/habits", json={"name": "Read 20 minutes"})
    assert r.status_code == 200
    hid = r.json()["id"]
    r2 = client.get("/habits")
    assert r2.status_code == 200
    assert any(h["id"] == hid for h in r2.json())


def test_checkin_flow():
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


def test_checkin_unknown_habit_404():
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404


def test_summary_with_zero_checkins(monkeypatch):
    monkeypatch.setattr(main, "date", FrozenDate)
    habit_id = client.post("/habits", json={"name": "No check-ins"}).json()["id"]

    response = client.get(f"/habits/{habit_id}/summary")

    assert response.status_code == 200
    assert response.json() == {"habit_id": habit_id, "count": 0}


def test_summary_counts_today_and_earliest_included_day(monkeypatch):
    monkeypatch.setattr(main, "date", FrozenDate)
    habit_id = client.post("/habits", json={"name": "Window boundaries"}).json()["id"]
    for day in ("2026-09-22", "2026-09-16"):
        assert (
            client.post(
                f"/habits/{habit_id}/checkin",
                json={"day": day},
            ).status_code
            == 200
        )

    response = client.get(f"/habits/{habit_id}/summary")

    assert response.status_code == 200
    assert response.json() == {"habit_id": habit_id, "count": 2}


def test_summary_excludes_day_just_outside_window(monkeypatch):
    monkeypatch.setattr(main, "date", FrozenDate)
    habit_id = client.post("/habits", json={"name": "Outside window"}).json()["id"]
    assert (
        client.post(
            f"/habits/{habit_id}/checkin",
            json={"day": "2026-09-15"},
        ).status_code
        == 200
    )

    response = client.get(f"/habits/{habit_id}/summary")

    assert response.status_code == 200
    assert response.json() == {"habit_id": habit_id, "count": 0}


def test_summary_counts_duplicate_checkins(monkeypatch):
    monkeypatch.setattr(main, "date", FrozenDate)
    habit_id = client.post("/habits", json={"name": "Duplicate check-ins"}).json()["id"]
    for _ in range(2):
        assert (
            client.post(
                f"/habits/{habit_id}/checkin",
                json={"day": "2026-09-22"},
            ).status_code
            == 200
        )

    response = client.get(f"/habits/{habit_id}/summary")

    assert response.status_code == 200
    assert response.json() == {"habit_id": habit_id, "count": 2}


def test_summary_unknown_habit_404():
    response = client.get("/habits/-1/summary")

    assert response.status_code == 404
    assert response.json() == {"detail": "unknown habit"}
