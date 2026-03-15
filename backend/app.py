from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from backend.config import Config
from backend.models import db, seed_defaults


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or Config)
    CORS(app)
    db.init_app(app)

    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
        db.create_all()
        seed_defaults(db.session)

        from backend.routes.settings import bp as settings_bp
        app.register_blueprint(settings_bp)

        from backend.routes.pet import bp as pet_bp
        app.register_blueprint(pet_bp)

        from backend.routes.habits import bp as habits_bp
        app.register_blueprint(habits_bp)

        from backend.routes.goals import bp as goals_bp
        app.register_blueprint(goals_bp)

        from backend.routes.mood import bp as mood_bp
        app.register_blueprint(mood_bp)

        from backend.routes.schedule import bp as schedule_bp
        app.register_blueprint(schedule_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
