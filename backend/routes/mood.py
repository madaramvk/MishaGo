from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from backend.models import db, MoodEntry

bp = Blueprint("mood", __name__, url_prefix="/api/mood")


@bp.route("", methods=["POST"])
def log_mood():
    data = request.get_json()
    entry = MoodEntry(date=date.today(), mood=data["mood"], energy=data["energy"], note=data.get("note", ""))
    db.session.add(entry)
    db.session.commit()
    return jsonify({"id": entry.id}), 201


@bp.route("", methods=["GET"])
def get_moods():
    days = int(request.args.get("days", 7))
    since = date.today() - timedelta(days=days)
    entries = MoodEntry.query.filter(MoodEntry.date >= since).order_by(MoodEntry.date).all()
    return jsonify([{
        "id": e.id, "date": e.date.isoformat(),
        "mood": e.mood, "energy": e.energy, "note": e.note,
    } for e in entries])
