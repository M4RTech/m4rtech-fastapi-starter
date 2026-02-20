def test_expected_bulk_replace_and_reconcile(client):
    # wrzucamy expected dla route/day
    payload = {
        "day": "2026-02-19",
        "route": 320,
        "items": ["gb123456789", "GB123456789A1", "GB123456789"],  # duplikat celowo
        "mode": "replace",
    }
    r = client.post("/api/v1/expected/bulk", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["expected_count"] == 2
    assert body["inserted"] == 2

    # brak skanów => missing = 2
    r = client.get("/api/v1/reconcile?day=2026-02-19&route=320")
    assert r.status_code == 200
    rec = r.json()
    assert rec["expected_count"] == 2
    assert rec["scanned_count"] == 0
    assert rec["missing_count"] == 2
    assert rec["extra_count"] == 0

    # zeskanuj jeden => missing = 1
    r = client.post("/api/v1/scan", json={"gb_number": "GB123456789", "route": 320, "day": "2026-02-19"})
    assert r.status_code in (200, 201)

    r = client.get("/api/v1/reconcile?day=2026-02-19&route=320")
    rec = r.json()
    assert rec["expected_count"] == 2
    assert rec["scanned_count"] == 1
    assert rec["missing_count"] == 1
    assert "GB123456789A1" in rec["missing"]

    # zeskanuj extra (nie ma na liście) => extra = 1
    r = client.post("/api/v1/scan", json={"gb_number": "GB999999999", "route": 320, "day": "2026-02-19"})
    assert r.status_code in (200, 201)

    r = client.get("/api/v1/reconcile?day=2026-02-19&route=320")
    rec = r.json()
    assert rec["extra_count"] == 1
    assert "GB999999999" in rec["extra"]

    # replace nową listą (reset)
    payload2 = {
        "day": "2026-02-19",
        "route": 320,
        "items": ["GB111111111"],
        "mode": "replace",
    }
    r = client.post("/api/v1/expected/bulk", json=payload2)
    assert r.status_code == 200
    assert r.json()["expected_count"] == 1

    # reconcile po replace: expected = 1, skany dalej są (bo to osobna tabela)
    r = client.get("/api/v1/reconcile?day=2026-02-19&route=320")
    rec = r.json()
    assert rec["expected_count"] == 1
