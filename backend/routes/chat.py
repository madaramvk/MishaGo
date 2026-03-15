import json
import re
import anthropic
from flask import Blueprint, Response, jsonify, request, stream_with_context, current_app
from backend.models import db, ChatMessage, Setting, Direction, Goal, Habit
from backend.ai_coach import build_messages


def process_setup_ready(text, app):
    """Parse SETUP_READY line and create goals/habits/settings."""
    match = re.search(r'SETUP_READY:\s*(.+)$', text, re.MULTILINE)
    if not match:
        return False

    raw = match.group(1)

    with app.app_context():
        # Parse name
        name_match = re.search(r'name=([^,]+)', raw)
        if name_match:
            name = name_match.group(1).strip()
            setting = Setting.query.get("name")
            if setting:
                setting.value = name
            else:
                db.session.add(Setting(key="name", value=name))

        # Parse wake time
        wake_match = re.search(r'wake=(\d{2}:\d{2})', raw)
        if wake_match:
            wake = wake_match.group(1)
            setting = Setting.query.get("wake_time")
            if setting:
                setting.value = wake
            else:
                db.session.add(Setting(key="wake_time", value=wake))

        # Parse goals
        goals_match = re.search(r'goals=\[([^\]]+)\]', raw)
        if goals_match:
            goal_names = [g.strip() for g in goals_match.group(1).split(',')]
            career_dir = Direction.query.filter_by(name="Career").first()
            for gname in goal_names:
                if gname:
                    db.session.add(Goal(
                        title=gname,
                        direction_id=career_dir.id if career_dir else 1,
                        created_by="gucci",
                    ))

        # Parse habits
        habits_match = re.search(r'habits=\[([^\]]+)\]', raw)
        if habits_match:
            habit_names = [h.strip() for h in habits_match.group(1).split(',')]
            health_dir = Direction.query.filter_by(name="Health").first()
            mind_dir = Direction.query.filter_by(name="Mind").first()
            xp_map = {"tiny": 3, "small": 5, "medium": 10}
            for hname in habit_names:
                if not hname:
                    continue
                # Guess direction from keywords
                lower = hname.lower()
                if any(w in lower for w in ['зарядк', 'workout', 'спорт', 'упражн', 'физ']):
                    dir_id = health_dir.id if health_dir else 2
                    icon = "💪"
                elif any(w in lower for w in ['чтен', 'read', 'книг']):
                    dir_id = mind_dir.id if mind_dir else 3
                    icon = "📚"
                elif any(w in lower for w in ['фокус', 'focus', 'концентр']):
                    dir_id = mind_dir.id if mind_dir else 3
                    icon = "🧠"
                else:
                    dir_id = 4  # Life
                    icon = "✨"
                db.session.add(Habit(
                    name=hname, direction_id=dir_id, icon=icon,
                    difficulty="small", xp_reward=5, frequency="daily",
                ))

        # Mark onboarded
        onboarded = Setting.query.get("onboarded")
        if onboarded:
            onboarded.value = "true"
        else:
            db.session.add(Setting(key="onboarded", value="true"))

        db.session.commit()

    return True

bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@bp.route("/history", methods=["GET"])
def chat_history():
    context_type = request.args.get("context_type", "general")
    goal_id = request.args.get("goal_id", type=int)
    limit = request.args.get("limit", 20, type=int)

    query = ChatMessage.query.filter_by(context_type=context_type)
    if goal_id:
        query = query.filter_by(goal_id=goal_id)
    messages = query.order_by(ChatMessage.created_at.desc()).limit(limit).all()

    return jsonify([{
        "id": m.id, "role": m.role, "content": m.content,
        "goal_id": m.goal_id, "created_at": m.created_at.isoformat(),
    } for m in reversed(messages)])


@bp.route("/stream", methods=["GET"])
def stream_chat():
    user_message = request.args.get("message", "")
    if not user_message:
        return jsonify({"error": "message required"}), 400

    api_key_setting = Setting.query.get("api_key")
    if not api_key_setting or not api_key_setting.value:
        return jsonify({"error": "API key not configured"}), 400

    # Save user message
    user_msg = ChatMessage(role="user", content=user_message, context_type="general")
    db.session.add(user_msg)
    db.session.commit()

    system, messages = build_messages(user_message, "general")

    app = current_app._get_current_object()

    def generate():
        client = anthropic.Anthropic(api_key=api_key_setting.value)
        full_response = ""
        try:
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=512,
                system=system,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield f"data: {json.dumps({'text': text})}\n\n"

            # Save Gucci's response
            with app.app_context():
                # Strip SETUP_READY line from visible message
                visible = re.sub(r'\s*SETUP_READY:.*$', '', full_response, flags=re.MULTILINE).strip()
                gucci_msg = ChatMessage(
                    role="gucci", content=visible, context_type="general"
                )
                db.session.add(gucci_msg)
                db.session.commit()

                # Check for onboarding completion
                setup_done = process_setup_ready(full_response, app)

            if setup_done:
                yield f"data: {json.dumps({'setup_complete': True})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@bp.route("/goal/<int:goal_id>/stream", methods=["GET"])
def stream_goal_chat(goal_id):
    user_message = request.args.get("message", "")
    if not user_message:
        return jsonify({"error": "message required"}), 400

    api_key_setting = Setting.query.get("api_key")
    if not api_key_setting or not api_key_setting.value:
        return jsonify({"error": "API key not configured"}), 400

    user_msg = ChatMessage(
        role="user", content=user_message,
        context_type="goal", goal_id=goal_id,
    )
    db.session.add(user_msg)
    db.session.commit()

    system, messages = build_messages(user_message, "goal", goal_id)

    app = current_app._get_current_object()

    def generate():
        client = anthropic.Anthropic(api_key=api_key_setting.value)
        full_response = ""
        try:
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=512,
                system=system,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield f"data: {json.dumps({'text': text})}\n\n"

            with app.app_context():
                gucci_msg = ChatMessage(
                    role="gucci", content=full_response,
                    context_type="goal", goal_id=goal_id,
                )
                db.session.add(gucci_msg)
                db.session.commit()
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
