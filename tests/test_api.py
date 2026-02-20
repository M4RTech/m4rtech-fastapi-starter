def test_health_ok(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_scan_rejects_invalid_prefix(client):
    r = client.post(
        "/api/v1/scan",
        json={"gb_number": "XX123456789", "route": 320},
    )
    assert r.status_code == 422

    body = r.json()
    assert body["detail"][0]["loc"] == ["body", "gb_number"]
    assert "Invalid GB number" in body["detail"][0]["msg"]


def test_scan_accepts_and_normalizes(client):
    r = client.post(
        "/api/v1/scan",
        json={"gb_number": " gb123456789a1  ", "route": 320},
    )
    assert r.status_code == 200

    data = r.json()
    assert data["received"] == "GB123456789A1"
    assert data["length"] == 13
    assert "id" in data


def test_scans_list_and_clear(client):
    client.post(
        "/api/v1/scan",
        json={"gb_number": "GB123456789", "route": 320},
    )
    client.post(
        "/api/v1/scan",
        json={"gb_number": "GB123456780A1", "route": 320},
    )

    r = client.get("/api/v1/scans?limit=10")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 2
    assert len(body["items"]) == 2

    r = client.delete("/api/v1/scans")
    assert r.status_code == 200
    assert r.json()["removed_count"] == 2

    r = client.get("/api/v1/scans?limit=10")
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_scan_duplicate_same_day_route_gb(client):
    payload = {
        "gb_number": "GB123456789A1",
        "route": 320,
        "day": "2026-02-19",
        "user": "m4rtech",
    }

    r1 = client.post("/api/v1/scan", json=payload)
    assert r1.status_code == 200

    r2 = client.post("/api/v1/scan", json=payload)
    assert r2.status_code == 409
    assert r2.json()["detail"] == "Duplicate scan for this route/day"
