import json
from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from backend.models import db, ScheduleBlock, Setting, Habit, Goal, Direction
from backend.ai_coach import build_context

bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")

SCHEDULE_PROMPT = """You are Gucci, generating a daily schedule for the user.

RULES:
- Start from their wake time
- Include active habits at appropriate times
- Include work blocks for active goals
- Leave breathing room — don't pack every hour
- Evening habits (reading) go before sleep

ENERGY AWARENESS:
- Morning (wake to wake+4h): HIGH energy → hardest tasks (deep work, learning, coding)
- Midday (wake+4h to wake+8h): MEDIUM energy → practical tasks (applications, proposals)
- Evening: LOW energy → light habits (reading, reflection)

INTENSITY MODES:
- If mode="light": fewer blocks, shorter durations, more free time. User is tired or struggling.
- If mode="normal": balanced schedule. Default.
- If mode="intense": pack it tight, longer blocks, every hour counts. User is motivated and believes they can push.

GOAL URGENCY:
- Goals with low progress AND deadlines → prioritize these
- Goals stuck at 0% for days → give them prime morning slots
- Don't waste the day — every block should move a goal forward

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
    mode = data.get("mode", "normal")  # light / normal / intense / auto

    # Auto mode: Gucci decides based on recent data
    if mode == "auto":
        from backend.models import MoodEntry, HabitLog
        week_ago = date.today() - timedelta(days=7)

        # Check recent mood average
        moods = MoodEntry.query.filter(MoodEntry.date >= week_ago).all()
        avg_mood = sum(m.mood for m in moods) / len(moods) if moods else 3

        # Check habit completion rate
        logs = HabitLog.query.filter(HabitLog.date >= week_ago).all()
        if logs:
            done_rate = sum(1 for l in logs if l.completed) / len(logs)
        else:
            done_rate = 0.5

        # Decide
        if avg_mood >= 4 and done_rate >= 0.7:
            mode = "intense"  # user is doing great, push harder
        elif avg_mood <= 2 or done_rate <= 0.3:
            mode = "light"  # user is struggling, go easy
        else:
            mode = "normal"
    tomorrow = date.fromisoformat(target_date_str) if target_date_str else date.today() + timedelta(days=1)

    # Build context for AI
    wake = Setting.query.get("wake_time")
    wake_time = wake.value if wake else "07:00"
    context = build_context()

    # Add goal progress details
    from backend.models import GoalStep
    goals = Goal.query.filter_by(status="active").all()
    goal_details = []
    for g in goals:
        steps = GoalStep.query.filter_by(goal_id=g.id).all()
        done = sum(1 for s in steps if s.status == "done")
        total = len(steps)
        next_step = next((s.title for s in steps if s.status != "done"), None)
        goal_details.append(f"  - {g.title}: {done}/{total} steps done. Next: {next_step or 'no steps'}")

    if goal_details:
        context += "\n\nGoal details:\n" + "\n".join(goal_details)

    # Add schedule history (what was done/skipped yesterday)
    yesterday = tomorrow - timedelta(days=1)
    yesterday_blocks = ScheduleBlock.query.filter_by(date=yesterday).all()
    if yesterday_blocks:
        done_count = sum(1 for b in yesterday_blocks if b.status == "done")
        skip_count = sum(1 for b in yesterday_blocks if b.status == "skipped")
        context += f"\n\nYesterday: {done_count} done, {skip_count} skipped out of {len(yesterday_blocks)} planned"

    context += f"\n\nWake time: {wake_time}"
    context += f"\nIntensity mode: {mode}"
    context += f"\nGenerate schedule for: {tomorrow.isoformat()}"

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
