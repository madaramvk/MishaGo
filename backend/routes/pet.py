from datetime import date, timedelta
from flask import Blueprint, jsonify
from backend.models import db, Pet, HabitLog, ChatMessage, ShadowInsight, Setting, Goal, Habit, XP_THRESHOLDS

bp = Blueprint("pet", __name__, url_prefix="/api/pet")


def calculate_mood():
    today = date.today()
    today_habits = HabitLog.query.filter_by(date=today, completed=True).count()
    if today_habits >= 3:
        return "happy"
    today_chat = ChatMessage.query.filter(
        ChatMessage.created_at >= today.isoformat()
    ).first()
    if today_chat:
        return "content"
    two_days_ago = today - timedelta(days=2)
    three_days_ago = today - timedelta(days=3)
    any_recent = HabitLog.query.filter(
        HabitLog.date >= two_days_ago, HabitLog.completed == True
    ).first()
    if not any_recent:
        any_very_recent = HabitLog.query.filter(
            HabitLog.date >= three_days_ago, HabitLog.completed == True
        ).first()
        if not any_very_recent:
            return "concerned"
        return "sleepy"
    return "cozy"


def calculate_garden_stage(xp):
    stage = 0
    for i, threshold in enumerate(XP_THRESHOLDS):
        if xp >= threshold:
            stage = i
    return stage


@bp.route("", methods=["GET"])
def get_pet():
    pet = Pet.query.first()
    pet.mood = calculate_mood()
    pet.garden_stage = calculate_garden_stage(pet.xp)
    db.session.commit()
    return jsonify({
        "name": pet.name, "mood": pet.mood, "xp": pet.xp,
        "aura_color": pet.aura_color, "garden_stage": pet.garden_stage,
        "accessories": pet.accessories,
    })


@bp.route("/mind", methods=["GET"])
def get_mind():
    """Gucci's internal state — what it knows, what it thinks."""
    # User profile
    profile = {}
    for key in ("name", "wake_time", "language", "onboarded"):
        s = Setting.query.get(key)
        if s:
            profile[key] = s.value

    # What Gucci knows about goals
    goals = Goal.query.filter_by(status="active").all()
    goals_info = [{"title": g.title, "progress": g.progress, "created_by": g.created_by} for g in goals]

    # What habits Gucci tracks
    habits = Habit.query.filter_by(active=True).all()
    habits_info = [{"name": h.name, "icon": h.icon, "frequency": h.frequency} for h in habits]

    # Shadow insights — what patterns Gucci detected
    insights = ShadowInsight.query.order_by(ShadowInsight.created_at.desc()).limit(10).all()
    insights_info = [{
        "type": i.insight_type,
        "content": i.content,
        "confidence": round(i.confidence, 2),
        "used": i.used,
    } for i in insights]

    # Mood reasoning
    mood = calculate_mood()
    today = date.today()
    today_habits = HabitLog.query.filter_by(date=today, completed=True).count()
    today_chats = ChatMessage.query.filter(ChatMessage.created_at >= today.isoformat()).count()
    mood_reason = f"mood={mood}: {today_habits} habits done today, {today_chats} chat messages today"

    # Recent chat count
    total_chats = ChatMessage.query.count()

    return jsonify({
        "profile": profile,
        "goals": goals_info,
        "habits": habits_info,
        "insights": insights_info,
        "mood_reasoning": mood_reason,
        "total_conversations": total_chats,
    })
