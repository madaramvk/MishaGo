from datetime import date


def test_create_schedule_block(client):
    resp = client.post("/api/schedule", json={
        "date": str(date.today()), "start_time": "07:00",
        "end_time": "08:00", "title": "Workout", "block_type": "habit",
    })
    assert resp.status_code == 201


def test_get_schedule(client):
    client.post("/api/schedule", json={
        "date": str(date.today()), "start_time": "07:00",
        "end_time": "08:00", "title": "Workout", "block_type": "habit",
    })
    resp = client.get(f"/api/schedule/{date.today()}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Workout"


def test_update_schedule_block_status(client):
    block = client.post("/api/schedule", json={
        "date": str(date.today()), "start_time": "09:00",
        "end_time": "10:00", "title": "Focus", "block_type": "goal",
    }).get_json()
    resp = client.put(f"/api/schedule/{block['id']}", json={"status": "done"})
    assert resp.status_code == 200
