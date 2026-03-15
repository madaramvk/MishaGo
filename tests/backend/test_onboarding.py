from unittest.mock import patch, MagicMock
import json


def test_onboarding_extract_creates_entities(client, db_session):
    """Test that extraction creates goals, habits, directions from mock AI response."""
    mock_response = {
        "directions": [
            {"name": "Career", "icon": "💼", "color": "#7EB8DA"},
        ],
        "goals": [
            {"title": "Launch Upwork", "direction": "Career"},
        ],
        "habits": [
            {"name": "Workout 20min", "icon": "💪", "direction": "Health",
             "difficulty": "small", "frequency": "daily"},
        ],
        "schedule_hints": {"wake_time": "06:00"},
    }

    from backend.models import Setting
    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.commit()

    with patch("backend.routes.onboarding.extract_from_conversation") as mock_extract:
        mock_extract.return_value = mock_response
        resp = client.post("/api/onboarding/extract", json={
            "messages": [
                {"role": "gucci", "content": "What are you working towards?"},
                {"role": "user", "content": "I want to start freelancing on Upwork"},
            ]
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["goals"]) >= 1
        assert len(data["habits"]) >= 1


def test_onboarding_sets_onboarded_flag(client, db_session):
    from backend.models import Setting
    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.commit()

    with patch("backend.routes.onboarding.extract_from_conversation") as mock_extract:
        mock_extract.return_value = {
            "directions": [], "goals": [], "habits": [],
            "schedule_hints": {},
        }
        client.post("/api/onboarding/extract", json={"messages": []})
        setting = Setting.query.get("onboarded")
        assert setting.value == "true"
