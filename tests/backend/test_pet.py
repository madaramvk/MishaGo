def test_get_pet_default(client):
    resp = client.get("/api/pet")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Gucci"
    assert data["xp"] == 0
    assert data["garden_stage"] == 0


def test_pet_mood_happy_after_habits(client, db_session):
    from backend.models import Habit, HabitLog, Direction
    from datetime import date
    d = Direction.query.first()
    for i in range(3):
        h = Habit(name=f"h{i}", direction_id=d.id)
        db_session.add(h)
        db_session.flush()
        db_session.add(HabitLog(habit_id=h.id, date=date.today(), completed=True))
    db_session.commit()
    resp = client.get("/api/pet")
    assert resp.get_json()["mood"] == "happy"
