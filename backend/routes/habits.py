from datetime import date, datetime
from flask import Blueprint, jsonify, request
from backend.models import db, Habit, HabitLog, Pet

bp = Blueprint("habits", __name__, url_prefix="/api/habits")

WEEKDAY_MAP = {"daily": list(range(7)), "weekdays": list(range(5)), "weekends": [5, 6]}


def is_habit_today(habit, target_date=None):
    d = target_date or date.today()
    weekday = d.weekday()
    if habit.frequency in WEEKDAY_MAP:
        return weekday in WEEKDAY_MAP[habit.frequency]
    if habit.frequency == "custom" and habit.custom_days:
        return str(weekday) in habit.custom_days.split(",")
    return True


@bp.route("", methods=["GET"])
def list_habits():
    today_only = request.args.get("today") == "true"
    habits = Habit.query.filter_by(active=True).all()
    if today_only:
        habits = [h for h in habits if is_habit_today(h)]
    return jsonify([{
        "id": h.id, "name": h.name, "icon": h.icon,
        "difficulty": h.difficulty, "xp_reward": h.xp_reward,
        "frequency": h.frequency, "direction_id": h.direction_id,
    } for h in habits])


@bp.route("", methods=["POST"])
def create_habit():
    data = request.get_json()
    xp_map = {"tiny": 3, "small": 5, "medium": 10}
    difficulty = data.get("difficulty", "small")
    h = Habit(
        name=data["name"], direction_id=data["direction_id"],
        icon=data.get("icon", "✨"), difficulty=difficulty,
        xp_reward=xp_map.get(difficulty, 5),
        frequency=data.get("frequency", "daily"),
        custom_days=data.get("custom_days", ""),
    )
    db.session.add(h)
    db.session.commit()
    return jsonify({"id": h.id, "name": h.name}), 201


@bp.route("/<int:habit_id>", methods=["PUT"])
def update_habit(habit_id):
    h = Habit.query.get_or_404(habit_id)
    data = request.get_json()
    for key in ("name", "icon", "difficulty", "frequency", "custom_days", "active"):
        if key in data:
            setattr(h, key, data[key])
    db.session.commit()
    return jsonify({"ok": True})


@bp.route("/log", methods=["POST"])
def log_habit():
    data = request.get_json()
    log_date = date.fromisoformat(data["date"])
    existing = HabitLog.query.filter_by(habit_id=data["habit_id"], date=log_date).first()
    if existing:
        existing.completed = data["completed"]
        existing.energy_level = data.get("energy_level")
        existing.logged_at = datetime.utcnow()
    else:
        existing = HabitLog(
            habit_id=data["habit_id"], date=log_date,
            completed=data["completed"], energy_level=data.get("energy_level"),
        )
        db.session.add(existing)
    if data["completed"] and not HabitLog.query.filter_by(habit_id=data["habit_id"], date=log_date).first():
        habit = Habit.query.get(data["habit_id"])
        pet = Pet.query.first()
        pet.xp += habit.xp_reward
    elif data["completed"]:
        habit = Habit.query.get(data["habit_id"])
        pet = Pet.query.first()
        pet.xp += habit.xp_reward
    db.session.commit()
    return jsonify({"ok": True, "xp": Pet.query.first().xp})


@bp.route("/log/<log_date>", methods=["GET"])
def get_logs(log_date):
    d = date.fromisoformat(log_date)
    logs = HabitLog.query.filter_by(date=d).all()
    return jsonify([{
        "id": l.id, "habit_id": l.habit_id,
        "completed": l.completed, "energy_level": l.energy_level,
    } for l in logs])
