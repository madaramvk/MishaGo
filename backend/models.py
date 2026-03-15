from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Setting(db.Model):
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text, nullable=True)


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default="Gucci")
    mood = db.Column(db.String(16), default="content")
    xp = db.Column(db.Integer, default=0)
    aura_color = db.Column(db.String(16), default="#C4A8E0")
    garden_stage = db.Column(db.Integer, default=0)
    accessories = db.Column(db.Text, default="[]")


class Direction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    icon = db.Column(db.String(8), nullable=False)
    color = db.Column(db.String(16), nullable=False)


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    direction_id = db.Column(db.Integer, db.ForeignKey("direction.id"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(16), default="active")
    progress = db.Column(db.Integer, default=0)
    created_by = db.Column(db.String(8), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    direction = db.relationship("Direction", backref="goals")
    steps = db.relationship("GoalStep", backref="goal", cascade="all, delete-orphan")


class GoalStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(8), default="todo")
    deadline = db.Column(db.Date, nullable=True)
    created_by = db.Column(db.String(8), default="user")
    order = db.Column(db.Integer, default=0)


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    direction_id = db.Column(db.Integer, db.ForeignKey("direction.id"), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    icon = db.Column(db.String(8), default="✨")
    difficulty = db.Column(db.String(8), default="small")
    xp_reward = db.Column(db.Integer, default=5)
    frequency = db.Column(db.String(16), default="daily")
    custom_days = db.Column(db.String(32), default="")
    active = db.Column(db.Boolean, default=True)
    direction = db.relationship("Direction", backref="habits")


class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habit.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    energy_level = db.Column(db.String(8), nullable=True)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    habit = db.relationship("Habit", backref="logs")


class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    mood = db.Column(db.Integer, nullable=False)
    energy = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ScheduleBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"), nullable=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habit.id"), nullable=True)
    direction_id = db.Column(db.Integer, db.ForeignKey("direction.id"), nullable=True)
    block_type = db.Column(db.String(8), default="custom")
    status = db.Column(db.String(8), default="planned")
    generated_by = db.Column(db.String(8), default="user")


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(8), nullable=False)
    content = db.Column(db.Text, nullable=False)
    context_type = db.Column(db.String(8), default="general")
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ShadowInsight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    insight_type = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, default=0.0)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


XP_THRESHOLDS = [0, 50, 150, 300, 500, 800, 1200, 1800, 2500, 3500]


def seed_defaults(db_session):
    """Create default directions and pet on first launch."""
    if not Pet.query.first():
        db_session.add(Pet(name="Gucci"))
    if not Direction.query.first():
        defaults = [
            Direction(name="Career", icon="💼", color="#7EB8DA"),
            Direction(name="Health", icon="💪", color="#9DD6A3"),
            Direction(name="Mind", icon="📚", color="#C4A8E0"),
            Direction(name="Life", icon="🌱", color="#F0C987"),
        ]
        db_session.add_all(defaults)
    if not Setting.query.get("onboarded"):
        db_session.add(Setting(key="onboarded", value="false"))
        db_session.add(Setting(key="language", value="en"))
        db_session.add(Setting(key="theme", value="dark"))
    db_session.commit()
