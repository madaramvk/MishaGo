from datetime import date, timedelta, datetime
from backend.models import (
    db, Habit, HabitLog, MoodEntry, Goal, GoalStep, ShadowInsight, ScheduleBlock,
)


def analyze_energy_patterns():
    """Detect if user is a morning or evening person based on habit log times."""
    two_weeks_ago = date.today() - timedelta(days=14)
    logs = HabitLog.query.filter(
        HabitLog.date >= two_weeks_ago,
        HabitLog.completed == True,
        HabitLog.logged_at.isnot(None),
    ).all()

    if len(logs) < 3:
        return None

    before_noon = sum(1 for l in logs if l.logged_at and l.logged_at.hour < 12)
    ratio = before_noon / len(logs)
    confidence = min(len(logs) / 14, 1.0)

    if ratio >= 0.7:
        return ShadowInsight(
            insight_type="energy_pattern",
            content="You tend to complete habits in the morning — you're a morning person.",
            confidence=confidence,
        )
    elif ratio <= 0.3:
        return ShadowInsight(
            insight_type="energy_pattern",
            content="You tend to complete habits in the evening — your energy peaks later in the day.",
            confidence=confidence,
        )
    return None


def analyze_avoidance():
    """Detect goals that are being avoided (no progress in 7+ days)."""
    active_goals = Goal.query.filter_by(status="active").all()
    insights = []

    for goal in active_goals:
        steps = GoalStep.query.filter_by(goal_id=goal.id).all()
        if not steps:
            continue

        done_steps = [s for s in steps if s.status == "done"]
        if len(done_steps) == len(steps):
            continue  # fully complete

        # Check if any step was completed in last 7 days
        # (We don't have a completed_at field, so check if goal has no recent activity)
        total = len(steps)
        done = len(done_steps)
        if done == 0 and total > 0:
            days_old = (date.today() - goal.created_at.date()).days if goal.created_at else 0
            if days_old >= 7:
                confidence = min(days_old / 14, 1.0)
                insights.append(ShadowInsight(
                    insight_type="avoidance_pattern",
                    content=f"The goal '{goal.title}' hasn't seen any progress since it was created.",
                    confidence=confidence,
                ))

    return insights


def analyze_mood_correlations():
    """Find habits that correlate with better moods."""
    two_weeks_ago = date.today() - timedelta(days=14)
    habits = Habit.query.filter_by(active=True).all()
    moods = MoodEntry.query.filter(MoodEntry.date >= two_weeks_ago).all()
    mood_by_date = {m.date: m.mood for m in moods}

    if len(moods) < 5:
        return []

    insights = []
    for habit in habits:
        logs = HabitLog.query.filter(
            HabitLog.habit_id == habit.id,
            HabitLog.date >= two_weeks_ago,
            HabitLog.completed == True,
        ).all()
        done_dates = {l.date for l in logs}

        mood_on_done = [mood_by_date[d] for d in done_dates if d in mood_by_date]
        mood_on_skip = [mood_by_date[d] for d in mood_by_date if d not in done_dates]

        if len(mood_on_done) >= 3 and len(mood_on_skip) >= 3:
            avg_done = sum(mood_on_done) / len(mood_on_done)
            avg_skip = sum(mood_on_skip) / len(mood_on_skip)
            delta = avg_done - avg_skip

            if delta > 0.5:
                sample_days = len(mood_on_done) + len(mood_on_skip)
                confidence = min(sample_days / 14, 1.0)
                insights.append(ShadowInsight(
                    insight_type="mood_activity_correlation",
                    content=f"You tend to feel better on days when you do '{habit.name}'.",
                    confidence=confidence,
                ))

    return insights


def analyze_schedule_adherence():
    """Compare planned schedule blocks to actual habit logs."""
    yesterday = date.today() - timedelta(days=1)
    blocks = ScheduleBlock.query.filter_by(date=yesterday, block_type="habit").all()
    if not blocks:
        return None

    done = sum(1 for b in blocks if b.status == "done")
    total = len(blocks)
    ratio = done / total if total > 0 else 1.0

    if ratio < 0.5:
        return ShadowInsight(
            insight_type="schedule_adherence",
            content=f"Yesterday's schedule didn't match reality — only {done}/{total} planned tasks were completed.",
            confidence=0.7,
        )
    return None


def analyze_streaks():
    """Track consecutive completion days per habit."""
    habits = Habit.query.filter_by(active=True).all()
    insights = []

    for habit in habits:
        streak = 0
        day = date.today()
        while True:
            log = HabitLog.query.filter_by(
                habit_id=habit.id, date=day, completed=True
            ).first()
            if not log:
                break
            streak += 1
            day -= timedelta(days=1)

        if streak >= 7:
            insights.append(ShadowInsight(
                insight_type="streak_pattern",
                content=f"You're on a {streak}-day streak with '{habit.name}' — that's real consistency!",
                confidence=min(streak / 14, 1.0),
            ))

    return insights


def analyze_all():
    """Run all analyses and save new insights. Returns list of new insights."""
    new_insights = []

    energy = analyze_energy_patterns()
    if energy:
        ShadowInsight.query.filter_by(insight_type="energy_pattern").delete()
        db.session.add(energy)
        new_insights.append(energy)

    avoidance = analyze_avoidance()
    if avoidance:
        ShadowInsight.query.filter_by(insight_type="avoidance_pattern").delete()
        for a in avoidance:
            db.session.add(a)
        new_insights.extend(avoidance)

    correlations = analyze_mood_correlations()
    if correlations:
        ShadowInsight.query.filter_by(insight_type="mood_activity_correlation").delete()
        for c in correlations:
            db.session.add(c)
        new_insights.extend(correlations)

    adherence = analyze_schedule_adherence()
    if adherence:
        ShadowInsight.query.filter_by(insight_type="schedule_adherence").delete()
        db.session.add(adherence)
        new_insights.append(adherence)

    streaks = analyze_streaks()
    if streaks:
        ShadowInsight.query.filter_by(insight_type="streak_pattern").delete()
        for s in streaks:
            db.session.add(s)
        new_insights.extend(streaks)

    db.session.commit()
    return new_insights
