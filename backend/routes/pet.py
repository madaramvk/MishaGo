from datetime import date, timedelta
from flask import Blueprint, jsonify
from backend.models import db, Pet, HabitLog, ChatMessage, XP_THRESHOLDS

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
