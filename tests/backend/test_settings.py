def test_get_settings(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["language"] == "en"
    assert data["theme"] == "dark"
    assert data["onboarded"] == "false"


def test_update_settings(client):
    resp = client.put("/api/settings", json={"theme": "light", "language": "ru"})
    assert resp.status_code == 200
    resp = client.get("/api/settings")
    data = resp.get_json()
    assert data["theme"] == "light"
    assert data["language"] == "ru"
