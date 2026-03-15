from unittest.mock import patch
from datetime import date, timedelta
import json


def test_generate_schedule(client, db_session):
    from backend.models import Setting, Habit, Goal, Direction

    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.add(Setting(key="wake_time", value="06:00"))
    d = Direction.query.first()
    db_session.add(Habit(name="Workout", direction_id=d.id, frequency="daily"))
    db_session.add(Goal(title="Upwork", direction_id=d.id))
    db_session.commit()

    mock_schedule = [
        {"start_time": "06:15", "end_time": "06:35", "title": "Workout",
         "block_type": "habit", "direction": "Health"},
        {"start_time": "07:00", "end_time": "08:00", "title": "Upwork proposals",
         "block_type": "goal", "direction": "Career"},
    ]

    with patch("backend.routes.schedule.generate_schedule_ai") as mock_gen:
        mock_gen.return_value = mock_schedule
        tomorrow = date.today() + timedelta(days=1)
        resp = client.post("/api/schedule/generate")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["blocks"]) >= 1
