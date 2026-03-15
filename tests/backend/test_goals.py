def test_list_directions(client):
    resp = client.get("/api/directions")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 4


def test_create_goal(client):
    dirs = client.get("/api/directions").get_json()
    resp = client.post("/api/goals", json={"title": "Launch Upwork", "direction_id": dirs[0]["id"]})
    assert resp.status_code == 201


def test_create_step_updates_progress(client):
    dirs = client.get("/api/directions").get_json()
    goal = client.post("/api/goals", json={"title": "Portfolio", "direction_id": dirs[0]["id"]}).get_json()
    client.post(f"/api/goals/{goal['id']}/steps", json={"title": "Step 1"})
    client.post(f"/api/goals/{goal['id']}/steps", json={"title": "Step 2"})
    steps = client.get(f"/api/goals/{goal['id']}/steps").get_json()
    client.put(f"/api/goals/{goal['id']}/steps/{steps[0]['id']}", json={"status": "done"})
    goal_data = client.get("/api/goals").get_json()
    assert goal_data[0]["progress"] == 50
