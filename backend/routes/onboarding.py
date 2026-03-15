import json
from flask import Blueprint, jsonify, request
from backend.models import db, Setting, Direction, Goal, Habit

bp = Blueprint("onboarding", __name__, url_prefix="/api/onboarding")

EXTRACTION_PROMPT = """Analyze this conversation and extract the user's goals, habits, and life directions.

Return ONLY valid JSON in this exact format:
{
  "directions": [{"name": "string", "icon": "emoji", "color": "#hex"}],
  "goals": [{"title": "string", "direction": "direction_name"}],
  "habits": [{"name": "string", "icon": "emoji", "direction": "direction_name", "difficulty": "tiny|small|medium", "frequency": "daily|weekdays|weekends"}],
  "schedule_hints": {"wake_time": "HH:MM"}
}

Only include what the user explicitly mentioned. Don't invent goals or habits they didn't discuss."""


def extract_from_conversation(messages, api_key):
    """Call Sonnet to extract structured data from onboarding conversation."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    conversation_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=EXTRACTION_PROMPT,
        messages=[{"role": "user", "content": conversation_text}],
    )

    text = response.content[0].text
    # Try to extract JSON from response
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise ValueError("Could not parse AI response as JSON")


@bp.route("/extract", methods=["POST"])
def extract():
    data = request.get_json()
    messages = data.get("messages", [])

    api_key_setting = Setting.query.get("api_key")
    if not api_key_setting or not api_key_setting.value:
        return jsonify({"error": "API key not configured"}), 400

    try:
        extracted = extract_from_conversation(messages, api_key_setting.value)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    created = {"directions": [], "goals": [], "habits": []}

    # Create directions (skip if they already exist by name)
    dir_map = {}
    existing_dirs = {d.name: d for d in Direction.query.all()}
    for d_data in extracted.get("directions", []):
        name = d_data["name"]
        if name in existing_dirs:
            dir_map[name] = existing_dirs[name]
        else:
            d = Direction(name=name, icon=d_data["icon"], color=d_data["color"])
            db.session.add(d)
            db.session.flush()
            dir_map[name] = d
            created["directions"].append(name)

    # Also map existing directions for goals/habits
    for d in Direction.query.all():
        dir_map[d.name] = d

    # Create goals
    for g_data in extracted.get("goals", []):
        direction = dir_map.get(g_data.get("direction"))
        if not direction:
            direction = Direction.query.first()
        g = Goal(
            title=g_data["title"],
            direction_id=direction.id,
            created_by="gucci",
        )
        db.session.add(g)
        db.session.flush()
        created["goals"].append({
            "id": g.id, "title": g.title, "direction_id": g.direction_id,
        })

    # Create habits
    xp_map = {"tiny": 3, "small": 5, "medium": 10}
    for h_data in extracted.get("habits", []):
        direction = dir_map.get(h_data.get("direction"))
        if not direction:
            direction = Direction.query.first()
        difficulty = h_data.get("difficulty", "small")
        h = Habit(
            name=h_data["name"],
            icon=h_data.get("icon", "✨"),
            direction_id=direction.id,
            difficulty=difficulty,
            xp_reward=xp_map.get(difficulty, 5),
            frequency=h_data.get("frequency", "daily"),
        )
        db.session.add(h)
        db.session.flush()
        created["habits"].append({
            "id": h.id, "name": h.name, "icon": h.icon,
            "direction_id": h.direction_id, "frequency": h.frequency,
        })

    # Update wake time if provided
    hints = extracted.get("schedule_hints", {})
    if hints.get("wake_time"):
        wake = Setting.query.get("wake_time")
        if wake:
            wake.value = hints["wake_time"]
        else:
            db.session.add(Setting(key="wake_time", value=hints["wake_time"]))

    # Mark as onboarded
    onboarded = Setting.query.get("onboarded")
    if onboarded:
        onboarded.value = "true"
    else:
        db.session.add(Setting(key="onboarded", value="true"))

    db.session.commit()
    return jsonify(created)
