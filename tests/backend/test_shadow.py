from datetime import date, timedelta


def test_energy_pattern_insight(app, db_session):
    from backend.models import Habit, HabitLog, Direction
    from backend.shadow_analyzer import analyze_all
    from datetime import datetime

    d = Direction.query.first()
    h = Habit(name="Workout", direction_id=d.id)
    db_session.add(h)
    db_session.flush()

    # Log 10 completions all before noon
    for i in range(10):
        log_date = date.today() - timedelta(days=i)
        db_session.add(HabitLog(
            habit_id=h.id, date=log_date, completed=True,
            logged_at=datetime(2026, 3, 15, 8, 0),  # 8 AM
        ))
    db_session.commit()

    insights = analyze_all()
    types = [i.insight_type for i in insights]
    assert "energy_pattern" in types


def test_avoidance_pattern_insight(app, db_session):
    from backend.models import Goal, GoalStep, Direction
    from backend.shadow_analyzer import analyze_all
    from datetime import datetime

    d = Direction.query.first()
    g1 = Goal(title="Active Goal", direction_id=d.id)
    g2 = Goal(title="Avoided Goal", direction_id=d.id,
              created_at=datetime(2026, 3, 1))  # 14 days ago
    db_session.add_all([g1, g2])
    db_session.flush()

    db_session.add(GoalStep(goal_id=g1.id, title="s1", status="done"))
    db_session.add(GoalStep(goal_id=g2.id, title="s2", status="todo"))
    db_session.commit()

    insights = analyze_all()
    types = [i.insight_type for i in insights]
    assert "avoidance_pattern" in types


def test_mood_activity_correlation(app, db_session):
    from backend.models import Habit, HabitLog, MoodEntry, Direction
    from backend.shadow_analyzer import analyze_all

    d = Direction.query.first()
    h = Habit(name="Run", direction_id=d.id)
    db_session.add(h)
    db_session.flush()

    # Days with habit done = mood 5, without = mood 2
    for i in range(14):
        day = date.today() - timedelta(days=i)
        if i % 2 == 0:
            db_session.add(HabitLog(habit_id=h.id, date=day, completed=True))
            db_session.add(MoodEntry(date=day, mood=5, energy=4))
        else:
            db_session.add(MoodEntry(date=day, mood=2, energy=2))
    db_session.commit()

    insights = analyze_all()
    types = [i.insight_type for i in insights]
    assert "mood_activity_correlation" in types
