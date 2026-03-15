import json
from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from backend.models import db, ScheduleBlock, Setting, Habit, Goal, Direction
from backend.ai_coach import build_context

bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")

SCHEDULE_PROMPT = """You are generating a daily schedule for the user based on their goals and habits.

Create a realistic schedule that:
- Starts from their wake time
- Includes their active habits at appropriate times
- Includes work blocks for their active goals
- Leaves breathing room (don't pack every hour)
- Ends with evening habits (reading, etc.)

Return ONLY valid JSON array:
[
  {"start_time": "HH:MM", "end_time": "HH:MM", "title": "string",
   "block_type": "habit|goal|custom", "direction": "direction_name"}
]

Do NOT include breaks/meals/free time — only actionable tasks."""


def generate_schedule_ai(api_key, context):
    """Call Sonnet to generate a daily schedule."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SCHEDULE_PROMPT,
        messages=[{"role": "user", "content": context}],
    )

    text = response.content[0].text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise ValueError("Could not parse schedule response")


@bp.route("/generate", methods=["POST"])
def generate_schedule():
    api_key_setting = Setting.query.get("api_key")
    if not api_key_setting or not api_key_setting.value:
        return jsonify({"error": "API key not configured"}), 400

    data = request.get_json(silent=True) or {}
    target_date_str = data.get("date")
    tomorrow = date.fromisoformat(target_date_str) if target_date_str else date.today() + timedelta(days=1)

    # Build context for AI
    wake = Setting.query.get("wake_time")
    wake_time = wake.value if wake else "07:00"
    context = build_context()
    context += f"\n\nWake time: {wake_time}\nGenerate schedule for: {tomorrow.isoformat()}"

    try:
        blocks_data = generate_schedule_ai(api_key_setting.value, context)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Clear existing generated blocks for tomorrow
    ScheduleBlock.query.filter_by(date=tomorrow, generated_by="gucci").delete()

    dir_map = {d.name.lower(): d for d in Direction.query.all()}
    habit_map = {h.name.lower(): h for h in Habit.query.filter_by(active=True).all()}
    goal_map = {g.title.lower(): g for g in Goal.query.filter_by(status="active").all()}

    # Keywords to guess direction
    dir_keywords = {
        "health": ["зарядк", "workout", "спорт", "физ", "упражн", "гигиен", "здоров"],
        "career": ["работ", "фриланс", "upwork", "портфолио", "career", "проект"],
        "mind": ["чтен", "read", "книг", "фокус", "focus", "учёб", "учеб"],
        "life": ["отдых", "прогулк", "медитац", "сон"],
    }

    def guess_direction(title):
        lower = title.lower()
        for dir_name, keywords in dir_keywords.items():
            if any(kw in lower for kw in keywords):
                return dir_map.get(dir_name)
        return None

    created = []
    for b in blocks_data:
        direction = dir_map.get(b.get("direction", "").lower())
        block_type = b.get("block_type", "custom")
        title_lower = b["title"].lower()

        # Link to habit or goal
        habit_id = None
        goal_id = None
        if block_type == "habit":
            for name, habit in habit_map.items():
                if name in title_lower or title_lower in name:
                    habit_id = habit.id
                    if not direction:
                        direction = Direction.query.get(habit.direction_id)
                    break
        elif block_type == "goal":
            for name, goal in goal_map.items():
                if name in title_lower or title_lower in name:
                    goal_id = goal.id
                    if not direction:
                        direction = Direction.query.get(goal.direction_id)
                    break

        # Fallback: guess direction from title keywords
        if not direction:
            direction = guess_direction(b["title"])

        block = ScheduleBlock(
            date=tomorrow,
            start_time=b["start_time"],
            end_time=b["end_time"],
            title=b["title"],
            block_type=block_type,
            direction_id=direction.id if direction else None,
            habit_id=habit_id,
            goal_id=goal_id,
            generated_by="gucci",
        )
        db.session.add(block)
        created.append(b)

    db.session.commit()
    return jsonify({"date": tomorrow.isoformat(), "blocks": created})


@bp.route("/<schedule_date>", methods=["GET"])
def get_schedule(schedule_date):
    d = date.fromisoformat(schedule_date)
    blocks = ScheduleBlock.query.filter_by(date=d).order_by(ScheduleBlock.start_time).all()
    return jsonify([{
        "id": b.id, "start_time": b.start_time, "end_time": b.end_time,
        "title": b.title, "block_type": b.block_type,
        "direction_id": b.direction_id, "goal_id": b.goal_id,
        "habit_id": b.habit_id, "status": b.status, "generated_by": b.generated_by,
    } for b in blocks])


@bp.route("", methods=["POST"])
def create_block():
    data = request.get_json()
    b = ScheduleBlock(
        date=date.fromisoformat(data["date"]), start_time=data["start_time"],
        end_time=data["end_time"], title=data["title"],
        block_type=data.get("block_type", "custom"),
        direction_id=data.get("direction_id"), goal_id=data.get("goal_id"),
        habit_id=data.get("habit_id"), generated_by=data.get("generated_by", "user"),
    )
    db.session.add(b)
    db.session.commit()
    return jsonify({"id": b.id}), 201


@bp.route("/<int:block_id>", methods=["PUT"])
def update_block(block_id):
    b = ScheduleBlock.query.get_or_404(block_id)
    data = request.get_json()
    for key in ("status", "start_time", "end_time", "title"):
        if key in data:
            setattr(b, key, data[key])
    db.session.commit()
    return jsonify({"ok": True})
