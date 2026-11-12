import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_and_list_habit():
    r = client.post("/habits", json={"name": "Read 20 minutes"})
    assert r.status_code == 200
    assert set(r.json()) == {"id", "name"}
    assert r.json()["name"] == "Read 20 minutes"
    hid = r.json()["id"]
    r2 = client.get("/habits")
    assert r2.status_code == 200
    assert any(h["id"] == hid for h in r2.json())


@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_create_habit_rejects_empty_or_whitespace_name(name):
    response = client.post("/habits", json={"name": name})

    assert response.status_code == 422
    assert "name must not be empty or whitespace" in response.text


def test_checkin_flow():
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "day": "2026-09-22"}
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


@pytest.mark.parametrize(
    "day",
    ["not-a-date", "2026-02-30", "2026-9-22", "09/22/2026", "20260230"],
)
def test_checkin_rejects_invalid_day(day):
    hid = client.post("/habits", json={"name": "Date validation"}).json()["id"]

    response = client.post(f"/habits/{hid}/checkin", json={"day": day})

    assert response.status_code == 422
    assert "day must be a real date in YYYY-MM-DD format" in response.text


def test_checkin_accepts_valid_calendar_date():
    hid = client.post("/habits", json={"name": "Leap day"}).json()["id"]

    response = client.post(f"/habits/{hid}/checkin", json={"day": "2024-02-29"})

    assert response.status_code == 200
    assert response.json() == {"habit_id": hid, "day": "2024-02-29"}


def test_checkin_unknown_habit_404():
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404
