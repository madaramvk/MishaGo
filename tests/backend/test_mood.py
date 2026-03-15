def test_log_mood(client):
    resp = client.post("/api/mood", json={"mood": 4, "energy": 3, "note": "good day"})
    assert resp.status_code == 201


def test_get_recent_moods(client):
    client.post("/api/mood", json={"mood": 4, "energy": 3})
    resp = client.get("/api/mood?days=7")
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1
