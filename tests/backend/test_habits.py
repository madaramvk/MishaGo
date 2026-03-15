from datetime import date


def test_create_habit(client, db_session):
    from backend.models import Direction
    d = Direction.query.first()
    resp = client.post("/api/habits", json={
        "name": "Workout", "direction_id": d.id,
        "icon": "💪", "difficulty": "small", "frequency": "daily"
    })
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Workout"


def test_list_habits(client, db_session):
    from backend.models import Direction, Habit
    d = Direction.query.first()
    db_session.add(Habit(name="Read", direction_id=d.id))
    db_session.commit()
    resp = client.get("/api/habits")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_log_habit_awards_xp(client, db_session):
    from backend.models import Direction, Habit, Pet
    d = Direction.query.first()
    h = Habit(name="Walk", direction_id=d.id, xp_reward=5)
    db_session.add(h)
    db_session.commit()
    resp = client.post("/api/habits/log", json={
        "habit_id": h.id, "date": str(date.today()), "completed": True
    })
    assert resp.status_code == 200
    pet = Pet.query.first()
    assert pet.xp == 5


def test_get_logs_for_date(client, db_session):
    from backend.models import Direction, Habit, HabitLog
    d = Direction.query.first()
    h = Habit(name="Focus", direction_id=d.id)
    db_session.add(h)
    db_session.flush()
    db_session.add(HabitLog(habit_id=h.id, date=date.today(), completed=True))
    db_session.commit()
    resp = client.get(f"/api/habits/log/{date.today()}")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1
