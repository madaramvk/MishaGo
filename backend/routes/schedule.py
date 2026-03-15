from datetime import date
from flask import Blueprint, jsonify, request
from backend.models import db, ScheduleBlock

bp = Blueprint("schedule", __name__, url_prefix="/api/schedule")


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
