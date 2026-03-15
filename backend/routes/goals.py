from flask import Blueprint, jsonify, request
from backend.models import db, Direction, Goal, GoalStep

bp = Blueprint("goals", __name__, url_prefix="/api")


@bp.route("/directions", methods=["GET"])
def list_directions():
    dirs = Direction.query.all()
    return jsonify([{"id": d.id, "name": d.name, "icon": d.icon, "color": d.color} for d in dirs])


@bp.route("/directions", methods=["POST"])
def create_direction():
    data = request.get_json()
    d = Direction(name=data["name"], icon=data["icon"], color=data["color"])
    db.session.add(d)
    db.session.commit()
    return jsonify({"id": d.id}), 201


@bp.route("/goals", methods=["GET"])
def list_goals():
    query = Goal.query
    direction_id = request.args.get("direction_id")
    status = request.args.get("status")
    if direction_id:
        query = query.filter_by(direction_id=int(direction_id))
    if status:
        query = query.filter_by(status=status)
    goals = query.all()
    return jsonify([{
        "id": g.id, "title": g.title, "description": g.description,
        "status": g.status, "progress": g.progress,
        "direction_id": g.direction_id, "created_by": g.created_by,
    } for g in goals])


@bp.route("/goals", methods=["POST"])
def create_goal():
    data = request.get_json()
    g = Goal(title=data["title"], direction_id=data["direction_id"],
             description=data.get("description", ""), created_by=data.get("created_by", "user"))
    db.session.add(g)
    db.session.commit()
    return jsonify({"id": g.id, "title": g.title}), 201


@bp.route("/goals/<int:goal_id>", methods=["PUT"])
def update_goal(goal_id):
    g = Goal.query.get_or_404(goal_id)
    data = request.get_json()
    for key in ("title", "description", "status"):
        if key in data:
            setattr(g, key, data[key])
    db.session.commit()
    return jsonify({"ok": True})


def recalculate_progress(goal):
    total = len(goal.steps)
    if total == 0:
        goal.progress = 0
    else:
        done = sum(1 for s in goal.steps if s.status == "done")
        goal.progress = int(done / total * 100)


@bp.route("/goals/<int:goal_id>/steps", methods=["GET"])
def list_steps(goal_id):
    steps = GoalStep.query.filter_by(goal_id=goal_id).order_by(GoalStep.order).all()
    return jsonify([{
        "id": s.id, "title": s.title, "status": s.status,
        "deadline": s.deadline.isoformat() if s.deadline else None,
        "order": s.order, "created_by": s.created_by,
    } for s in steps])


@bp.route("/goals/<int:goal_id>/steps", methods=["POST"])
def create_step(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    data = request.get_json()
    max_order = db.session.query(db.func.max(GoalStep.order)).filter_by(goal_id=goal_id).scalar() or 0
    step = GoalStep(goal_id=goal_id, title=data["title"], deadline=data.get("deadline"),
                    created_by=data.get("created_by", "user"), order=max_order + 1)
    db.session.add(step)
    db.session.flush()
    recalculate_progress(goal)
    db.session.commit()
    return jsonify({"id": step.id}), 201


@bp.route("/goals/<int:goal_id>/steps/<int:step_id>", methods=["PUT"])
def update_step(goal_id, step_id):
    step = GoalStep.query.get_or_404(step_id)
    goal = Goal.query.get_or_404(goal_id)
    data = request.get_json()
    for key in ("title", "status", "deadline", "order"):
        if key in data:
            setattr(step, key, data[key])
    recalculate_progress(goal)
    db.session.commit()
    return jsonify({"ok": True})
