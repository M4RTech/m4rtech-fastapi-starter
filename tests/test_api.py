from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_scan_rejects_invalid_prefix():
    r = client.post("/api/v1/scan", json={"gb_number": "XX123"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Invalid GB number"


def test_scan_accepts_and_normalizes():
    r = client.post("/api/v1/scan", json={"gb_number": " gb12345  "})
    assert r.status_code == 200

    data = r.json()
    assert data["received"] == "GB12345"
    assert data["length"] == 7
    assert data["status"] == "ok"
    assert data["saved"] is True
    assert "id" in data


def test_scans_list_and_clear():
    # Dodaj 2 skany
    client.post("/api/v1/scan", json={"gb_number": "GB1"})
    client.post("/api/v1/scan", json={"gb_number": "GB2"})

    # Pobierz listę
    r = client.get("/api/v1/scans?limit=10")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert body["count"] >= 2

    # Wyczyść
    r = client.delete("/api/v1/scans")
    assert r.status_code == 200
    assert r.json()["cleared"] is True

    # Po czyszczeniu lista pusta
    r = client.get("/api/v1/scans?limit=10")
    assert r.status_code == 200
    assert r.json()["count"] == 0
