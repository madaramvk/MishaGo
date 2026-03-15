from flask import Blueprint, jsonify, request
from backend.models import db, Setting

bp = Blueprint("settings", __name__, url_prefix="/api/settings")


@bp.route("", methods=["GET"])
def get_settings():
    rows = Setting.query.all()
    return jsonify({r.key: r.value for r in rows})


@bp.route("", methods=["PUT"])
def update_settings():
    data = request.get_json()
    for key, value in data.items():
        setting = Setting.query.get(key)
        if setting:
            setting.value = str(value)
        else:
            db.session.add(Setting(key=key, value=str(value)))
    db.session.commit()
    return jsonify({"ok": True})
