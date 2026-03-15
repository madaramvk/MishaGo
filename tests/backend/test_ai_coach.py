from unittest.mock import patch, MagicMock


def test_build_system_prompt(app):
    with app.app_context():
        from backend.ai_coach import build_system_prompt
        prompt = build_system_prompt(language="en")
        assert "Gucci" in prompt
        assert "spirit companion" in prompt


def test_build_system_prompt_russian(app):
    with app.app_context():
        from backend.ai_coach import build_system_prompt
        prompt = build_system_prompt(language="ru")
        assert "русском" in prompt.lower() or "Russian" in prompt


def test_build_context(app, db_session):
    with app.app_context():
        from backend.ai_coach import build_context
        from backend.models import MoodEntry, Setting
        from datetime import date
        db_session.add(MoodEntry(date=date.today(), mood=4, energy=3))
        db_session.commit()
        context = build_context()
        assert "mood" in context.lower() or "4" in context


def test_build_goal_context(app, db_session):
    with app.app_context():
        from backend.ai_coach import build_goal_context
        from backend.models import Goal, Direction
        d = Direction.query.first()
        g = Goal(title="Test Goal", direction_id=d.id)
        db_session.add(g)
        db_session.commit()
        context = build_goal_context(g.id)
        assert "Test Goal" in context
