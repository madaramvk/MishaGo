import json
import anthropic
from flask import Blueprint, Response, jsonify, request, stream_with_context, current_app
from backend.models import db, ChatMessage, Setting
from backend.ai_coach import build_messages

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
                model="claude-sonnet-4-6-20250514",
                max_tokens=512,
                system=system,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield f"data: {json.dumps({'text': text})}\n\n"

            # Save Gucci's response
            with app.app_context():
                gucci_msg = ChatMessage(
                    role="gucci", content=full_response, context_type="general"
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
                model="claude-sonnet-4-6-20250514",
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
