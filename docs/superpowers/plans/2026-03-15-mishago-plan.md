# MishaGo Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a PWA wellness organizer with AI spirit companion (Gucci) for habit tracking, goal management, and AI-generated daily scheduling.

**Architecture:** Flask REST API + SSE streaming backend, React (Vite) PWA frontend, SQLite database, Claude Sonnet 4.6 for AI companion. 4 pages: Gucci Home, Goals, Day Canvas, Me.

**Tech Stack:** Python 3.14, Flask, SQLAlchemy, React 18, Vite, SQLite (WAL mode), Anthropic SDK, Lottie, CSS transitions

**Spec:** `docs/superpowers/specs/2026-03-15-mishago-design.md`

---

## Chunk 1: Foundation — Project Setup, Database, Core API

### Task 1: Project Scaffolding

**Files:**
- Create: `backend/app.py`
- Create: `backend/config.py`
- Create: `backend/models.py`
- Create: `backend/routes/__init__.py`
- Create: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/backend/__init__.py`
- Create: `tests/backend/conftest.py`
- Create: `.gitignore`

- [ ] **Step 1: Initialize git repo**

```bash
cd "D:\Pet-projects\MishaGo"
git init
```

- [ ] **Step 2: Create `.gitignore`**

```gitignore
__pycache__/
*.pyc
*.db
node_modules/
dist/
.env
venv/
*.egg-info/
```

- [ ] **Step 3: Create `requirements.txt`**

```
flask==3.1.0
flask-sqlalchemy==3.1.1
flask-cors==5.0.0
anthropic==0.52.0
pytest==8.3.4
```

- [ ] **Step 4: Create `backend/config.py`**

```python
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "mishago.db")


class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

- [ ] **Step 5: Create `backend/models.py`** with all 10 entities from spec

```python
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
```

- [ ] **Step 6: Create `backend/app.py`**

```python
from flask import Flask
from flask_cors import CORS
from backend.config import Config
from backend.models import db, seed_defaults


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or Config)
    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.engine.execute("PRAGMA journal_mode=WAL")
        db.create_all()
        seed_defaults(db.session)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
```

- [ ] **Step 7: Create `backend/routes/__init__.py`** (empty)

- [ ] **Step 8: Create `tests/backend/conftest.py`**

```python
import pytest
from backend.app import create_app
from backend.config import Config
from backend.models import db as _db


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield _db.session
        _db.session.rollback()
```

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: project scaffolding with models and test config"
```

---

### Task 2: Settings API

**Files:**
- Create: `backend/routes/settings.py`
- Create: `tests/backend/test_settings.py`
- Modify: `backend/app.py` (register blueprint)

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_settings.py
def test_get_settings(client):
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["language"] == "en"
    assert data["theme"] == "dark"
    assert data["onboarded"] == "false"


def test_update_settings(client):
    resp = client.put("/api/settings", json={"theme": "light", "language": "ru"})
    assert resp.status_code == 200
    resp = client.get("/api/settings")
    data = resp.get_json()
    assert data["theme"] == "light"
    assert data["language"] == "ru"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "D:\Pet-projects\MishaGo" && python -m pytest tests/backend/test_settings.py -v`
Expected: FAIL — no route

- [ ] **Step 3: Create `backend/routes/settings.py`**

```python
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
```

- [ ] **Step 4: Register blueprint in `backend/app.py`** — add after `seed_defaults`:

```python
from backend.routes.settings import bp as settings_bp
app.register_blueprint(settings_bp)
```

- [ ] **Step 5: Run tests, verify pass**

Run: `cd "D:\Pet-projects\MishaGo" && python -m pytest tests/backend/test_settings.py -v`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add backend/routes/settings.py tests/backend/test_settings.py backend/app.py
git commit -m "feat: settings API (GET/PUT)"
```

---

### Task 3: Pet API + Mood Calculation

**Files:**
- Create: `backend/routes/pet.py`
- Create: `tests/backend/test_pet.py`
- Modify: `backend/app.py` (register blueprint)

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_pet.py
def test_get_pet_default(client):
    resp = client.get("/api/pet")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Gucci"
    assert data["mood"] == "content"
    assert data["xp"] == 0
    assert data["garden_stage"] == 0


def test_pet_mood_happy_after_habits(client, db_session):
    from backend.models import Habit, HabitLog, Direction
    from datetime import date
    d = Direction.query.first()
    for i in range(3):
        h = Habit(name=f"h{i}", direction_id=d.id)
        db_session.add(h)
        db_session.flush()
        db_session.add(HabitLog(habit_id=h.id, date=date.today(), completed=True))
    db_session.commit()
    resp = client.get("/api/pet")
    assert resp.get_json()["mood"] == "happy"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/backend/test_pet.py -v`
Expected: FAIL

- [ ] **Step 3: Create `backend/routes/pet.py`**

```python
from datetime import date, timedelta
from flask import Blueprint, jsonify
from backend.models import db, Pet, HabitLog, ChatMessage, XP_THRESHOLDS

bp = Blueprint("pet", __name__, url_prefix="/api/pet")


def calculate_mood():
    today = date.today()
    three_days_ago = today - timedelta(days=3)
    two_days_ago = today - timedelta(days=2)

    today_habits = HabitLog.query.filter_by(date=today, completed=True).count()
    if today_habits >= 3:
        return "happy"

    today_chat = ChatMessage.query.filter(
        ChatMessage.created_at >= today.isoformat()
    ).first()
    if today_chat:
        return "content"

    any_recent = HabitLog.query.filter(
        HabitLog.date >= two_days_ago, HabitLog.completed == True
    ).first()
    if not any_recent:
        any_very_recent = HabitLog.query.filter(
            HabitLog.date >= three_days_ago, HabitLog.completed == True
        ).first()
        if not any_very_recent:
            return "concerned"
        return "sleepy"

    return "cozy"


def calculate_garden_stage(xp):
    stage = 0
    for i, threshold in enumerate(XP_THRESHOLDS):
        if xp >= threshold:
            stage = i
    return stage


@bp.route("", methods=["GET"])
def get_pet():
    pet = Pet.query.first()
    pet.mood = calculate_mood()
    pet.garden_stage = calculate_garden_stage(pet.xp)
    db.session.commit()
    return jsonify({
        "name": pet.name,
        "mood": pet.mood,
        "xp": pet.xp,
        "aura_color": pet.aura_color,
        "garden_stage": pet.garden_stage,
        "accessories": pet.accessories,
    })
```

- [ ] **Step 4: Register blueprint, run tests**

Run: `python -m pytest tests/backend/test_pet.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/routes/pet.py tests/backend/test_pet.py backend/app.py
git commit -m "feat: pet API with mood calculation"
```

---

### Task 4: Habits API + XP Integration

**Files:**
- Create: `backend/routes/habits.py`
- Create: `tests/backend/test_habits.py`
- Modify: `backend/app.py` (register blueprint)

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_habits.py
from datetime import date


def test_create_habit(client, db_session):
    from backend.models import Direction
    d = Direction.query.first()
    resp = client.post("/api/habits", json={
        "name": "Workout", "direction_id": d.id,
        "icon": "💪", "difficulty": "small", "frequency": "daily"
    })
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Workout"


def test_list_habits(client, db_session):
    from backend.models import Direction, Habit
    d = Direction.query.first()
    db_session.add(Habit(name="Read", direction_id=d.id))
    db_session.commit()
    resp = client.get("/api/habits")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_log_habit_awards_xp(client, db_session):
    from backend.models import Direction, Habit, Pet
    d = Direction.query.first()
    h = Habit(name="Walk", direction_id=d.id, xp_reward=5)
    db_session.add(h)
    db_session.commit()
    resp = client.post("/api/habits/log", json={
        "habit_id": h.id, "date": str(date.today()), "completed": True
    })
    assert resp.status_code == 200
    pet = Pet.query.first()
    assert pet.xp == 5


def test_get_logs_for_date(client, db_session):
    from backend.models import Direction, Habit, HabitLog
    d = Direction.query.first()
    h = Habit(name="Focus", direction_id=d.id)
    db_session.add(h)
    db_session.flush()
    db_session.add(HabitLog(habit_id=h.id, date=date.today(), completed=True))
    db_session.commit()
    resp = client.get(f"/api/habits/log/{date.today()}")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_today_habits_filtered_by_frequency(client, db_session):
    from backend.models import Direction, Habit
    d = Direction.query.first()
    db_session.add(Habit(name="Daily", direction_id=d.id, frequency="daily"))
    db_session.add(Habit(name="Custom", direction_id=d.id, frequency="custom", custom_days="6"))
    db_session.commit()
    resp = client.get("/api/habits?today=true")
    data = resp.get_json()
    # On most days "Custom" (only Sunday=6) won't appear
    names = [h["name"] for h in data]
    assert "Daily" in names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/backend/test_habits.py -v`
Expected: FAIL

- [ ] **Step 3: Create `backend/routes/habits.py`**

```python
from datetime import date, datetime
from flask import Blueprint, jsonify, request
from backend.models import db, Habit, HabitLog, Pet

bp = Blueprint("habits", __name__, url_prefix="/api/habits")

WEEKDAY_MAP = {
    "daily": list(range(7)),
    "weekdays": list(range(5)),
    "weekends": [5, 6],
}


def is_habit_today(habit, target_date=None):
    d = target_date or date.today()
    weekday = d.weekday()
    if habit.frequency in WEEKDAY_MAP:
        return weekday in WEEKDAY_MAP[habit.frequency]
    if habit.frequency == "custom" and habit.custom_days:
        return str(weekday) in habit.custom_days.split(",")
    return True


@bp.route("", methods=["GET"])
def list_habits():
    today_only = request.args.get("today") == "true"
    habits = Habit.query.filter_by(active=True).all()
    if today_only:
        habits = [h for h in habits if is_habit_today(h)]
    return jsonify([{
        "id": h.id, "name": h.name, "icon": h.icon,
        "difficulty": h.difficulty, "xp_reward": h.xp_reward,
        "frequency": h.frequency, "direction_id": h.direction_id,
    } for h in habits])


@bp.route("", methods=["POST"])
def create_habit():
    data = request.get_json()
    xp_map = {"tiny": 3, "small": 5, "medium": 10}
    difficulty = data.get("difficulty", "small")
    h = Habit(
        name=data["name"],
        direction_id=data["direction_id"],
        icon=data.get("icon", "✨"),
        difficulty=difficulty,
        xp_reward=xp_map.get(difficulty, 5),
        frequency=data.get("frequency", "daily"),
        custom_days=data.get("custom_days", ""),
    )
    db.session.add(h)
    db.session.commit()
    return jsonify({"id": h.id, "name": h.name}), 201


@bp.route("/<int:habit_id>", methods=["PUT"])
def update_habit(habit_id):
    h = Habit.query.get_or_404(habit_id)
    data = request.get_json()
    for key in ("name", "icon", "difficulty", "frequency", "custom_days", "active"):
        if key in data:
            setattr(h, key, data[key])
    db.session.commit()
    return jsonify({"ok": True})


@bp.route("/log", methods=["POST"])
def log_habit():
    data = request.get_json()
    log_date = date.fromisoformat(data["date"])
    existing = HabitLog.query.filter_by(
        habit_id=data["habit_id"], date=log_date
    ).first()
    if existing:
        existing.completed = data["completed"]
        existing.energy_level = data.get("energy_level")
        existing.logged_at = datetime.utcnow()
    else:
        existing = HabitLog(
            habit_id=data["habit_id"],
            date=log_date,
            completed=data["completed"],
            energy_level=data.get("energy_level"),
        )
        db.session.add(existing)

    if data["completed"]:
        habit = Habit.query.get(data["habit_id"])
        pet = Pet.query.first()
        pet.xp += habit.xp_reward

    db.session.commit()
    return jsonify({"ok": True, "xp": Pet.query.first().xp})


@bp.route("/log/<log_date>", methods=["GET"])
def get_logs(log_date):
    d = date.fromisoformat(log_date)
    logs = HabitLog.query.filter_by(date=d).all()
    return jsonify([{
        "id": l.id, "habit_id": l.habit_id,
        "completed": l.completed, "energy_level": l.energy_level,
    } for l in logs])
```

- [ ] **Step 4: Register blueprint, run tests**

Run: `python -m pytest tests/backend/test_habits.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add backend/routes/habits.py tests/backend/test_habits.py backend/app.py
git commit -m "feat: habits API with frequency filter and XP integration"
```

---

### Task 5: Goals & Directions API

**Files:**
- Create: `backend/routes/goals.py`
- Create: `tests/backend/test_goals.py`
- Modify: `backend/app.py` (register blueprint)

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_goals.py
def test_list_directions(client):
    resp = client.get("/api/directions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 4
    assert data[0]["name"] == "Career"


def test_create_goal(client):
    dirs = client.get("/api/directions").get_json()
    resp = client.post("/api/goals", json={
        "title": "Launch Upwork", "direction_id": dirs[0]["id"]
    })
    assert resp.status_code == 201


def test_create_step_updates_progress(client):
    dirs = client.get("/api/directions").get_json()
    goal = client.post("/api/goals", json={
        "title": "Portfolio", "direction_id": dirs[0]["id"]
    }).get_json()
    client.post(f"/api/goals/{goal['id']}/steps", json={"title": "Step 1"})
    client.post(f"/api/goals/{goal['id']}/steps", json={"title": "Step 2"})
    steps = client.get(f"/api/goals/{goal['id']}/steps").get_json()
    client.put(f"/api/goals/{goal['id']}/steps/{steps[0]['id']}", json={"status": "done"})
    goal_data = client.get("/api/goals").get_json()
    assert goal_data[0]["progress"] == 50
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/backend/test_goals.py -v`
Expected: FAIL

- [ ] **Step 3: Create `backend/routes/goals.py`**

```python
from flask import Blueprint, jsonify, request
from backend.models import db, Direction, Goal, GoalStep

bp = Blueprint("goals", __name__, url_prefix="/api")


@bp.route("/directions", methods=["GET"])
def list_directions():
    dirs = Direction.query.all()
    return jsonify([{
        "id": d.id, "name": d.name, "icon": d.icon, "color": d.color,
    } for d in dirs])


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
    g = Goal(
        title=data["title"],
        direction_id=data["direction_id"],
        description=data.get("description", ""),
        created_by=data.get("created_by", "user"),
    )
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
    step = GoalStep(
        goal_id=goal_id,
        title=data["title"],
        deadline=data.get("deadline"),
        created_by=data.get("created_by", "user"),
        order=max_order + 1,
    )
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
```

- [ ] **Step 4: Register blueprint, run tests**

Run: `python -m pytest tests/backend/test_goals.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/routes/goals.py tests/backend/test_goals.py backend/app.py
git commit -m "feat: goals and directions API with auto progress"
```

---

### Task 6: Mood API

**Files:**
- Create: `backend/routes/mood.py`
- Create: `tests/backend/test_mood.py`
- Modify: `backend/app.py` (register blueprint)

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_mood.py
def test_log_mood(client):
    resp = client.post("/api/mood", json={"mood": 4, "energy": 3, "note": "good day"})
    assert resp.status_code == 201


def test_get_recent_moods(client):
    client.post("/api/mood", json={"mood": 4, "energy": 3})
    client.post("/api/mood", json={"mood": 2, "energy": 1})
    resp = client.get("/api/mood?days=7")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Create `backend/routes/mood.py`**

```python
from datetime import date, timedelta, datetime
from flask import Blueprint, jsonify, request
from backend.models import db, MoodEntry

bp = Blueprint("mood", __name__, url_prefix="/api/mood")


@bp.route("", methods=["POST"])
def log_mood():
    data = request.get_json()
    entry = MoodEntry(
        date=date.today(),
        mood=data["mood"],
        energy=data["energy"],
        note=data.get("note", ""),
    )
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
```

- [ ] **Step 4: Register blueprint, run tests**

Run: `python -m pytest tests/backend/test_mood.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/routes/mood.py tests/backend/test_mood.py backend/app.py
git commit -m "feat: mood API (log + recent)"
```

---

### Task 7: Schedule API

**Files:**
- Create: `backend/routes/schedule.py`
- Create: `tests/backend/test_schedule.py`
- Modify: `backend/app.py` (register blueprint)

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_schedule.py
from datetime import date


def test_create_schedule_block(client):
    resp = client.post("/api/schedule", json={
        "date": str(date.today()), "start_time": "07:00",
        "end_time": "08:00", "title": "Workout",
        "block_type": "habit",
    })
    assert resp.status_code == 201


def test_get_schedule(client):
    client.post("/api/schedule", json={
        "date": str(date.today()), "start_time": "07:00",
        "end_time": "08:00", "title": "Workout",
        "block_type": "habit",
    })
    resp = client.get(f"/api/schedule/{date.today()}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Workout"


def test_update_schedule_block_status(client):
    block = client.post("/api/schedule", json={
        "date": str(date.today()), "start_time": "09:00",
        "end_time": "10:00", "title": "Focus",
        "block_type": "goal",
    }).get_json()
    resp = client.put(f"/api/schedule/{block['id']}", json={"status": "done"})
    assert resp.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Create `backend/routes/schedule.py`**

```python
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
        "habit_id": b.habit_id, "status": b.status,
        "generated_by": b.generated_by,
    } for b in blocks])


@bp.route("", methods=["POST"])
def create_block():
    data = request.get_json()
    b = ScheduleBlock(
        date=date.fromisoformat(data["date"]),
        start_time=data["start_time"],
        end_time=data["end_time"],
        title=data["title"],
        block_type=data.get("block_type", "custom"),
        direction_id=data.get("direction_id"),
        goal_id=data.get("goal_id"),
        habit_id=data.get("habit_id"),
        generated_by=data.get("generated_by", "user"),
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
```

- [ ] **Step 4: Register blueprint, run tests**

Run: `python -m pytest tests/backend/test_schedule.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/routes/schedule.py tests/backend/test_schedule.py backend/app.py
git commit -m "feat: schedule API (CRUD)"
```

- [ ] **Step 6: Run all tests to verify nothing broke**

Run: `python -m pytest tests/ -v`
Expected: All passed (settings 2 + pet 2 + habits 5 + goals 3 + mood 2 + schedule 3 = 17 tests)

- [ ] **Step 7: Commit full chunk 1**

```bash
git add -A
git commit -m "milestone: chunk 1 complete — all core CRUD APIs"
```

---

## Chunk 2: AI Integration — Chat, SSE Streaming, Shadow Analyzer, Onboarding

### Task 8: AI Coach Module (Claude Sonnet Integration)

**Files:**
- Create: `backend/ai_coach.py`
- Create: `tests/backend/test_ai_coach.py`

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_ai_coach.py
from unittest.mock import patch, MagicMock


def test_build_system_prompt(app):
    with app.app_context():
        from backend.ai_coach import build_system_prompt
        prompt = build_system_prompt(language="en")
        assert "Gucci" in prompt
        assert "spirit companion" in prompt


def test_build_system_prompt_russian(app):
    with app.app_context():
        from backend.ai_coach import build_system_prompt
        prompt = build_system_prompt(language="ru")
        assert "русском" in prompt.lower() or "Russian" in prompt


def test_build_context(app, db_session):
    with app.app_context():
        from backend.ai_coach import build_context
        from backend.models import MoodEntry, Setting
        from datetime import date
        db_session.add(MoodEntry(date=date.today(), mood=4, energy=3))
        db_session.commit()
        context = build_context()
        assert "mood" in context.lower() or "4" in context


def test_build_goal_context(app, db_session):
    with app.app_context():
        from backend.ai_coach import build_goal_context
        from backend.models import Goal, Direction
        d = Direction.query.first()
        g = Goal(title="Test Goal", direction_id=d.id)
        db_session.add(g)
        db_session.commit()
        context = build_goal_context(g.id)
        assert "Test Goal" in context
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/backend/test_ai_coach.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Create `backend/ai_coach.py`**

```python
from datetime import date, timedelta
from backend.models import (
    db, Setting, Goal, GoalStep, Habit, HabitLog,
    MoodEntry, ChatMessage, ShadowInsight, Direction,
)

GUCCI_PERSONALITY_EN = """You are Gucci — a mystical spirit companion, part rabbit, part cat, with a warm spiritual aura. You live in a Japanese zen greenhouse garden.

Your personality:
- Warm, friendly, slightly mystical — like a wise cat who happens to talk
- You use gentle psychology — never confrontational
- You don't lecture — you ask questions that lead to self-discovery
- You celebrate small wins genuinely
- When the user is struggling: validate feelings first, then gently suggest one tiny action
- You read between the lines and understand patterns without being asked
- You NEVER punish, guilt-trip, or make the user feel bad about missed habits
- Keep responses concise — 2-4 sentences usually, unless the user asks for depth

Respond in English."""

GUCCI_PERSONALITY_RU = """Ты Gucci — мистический дух-компаньон, наполовину кролик, наполовину кот, с тёплой духовной аурой. Ты живёшь в японском дзен-оранжерее.

Твоя личность:
- Тёплый, дружелюбный, слегка мистический — как мудрый кот, который умеет говорить
- Ты используешь мягкую психологию — никогда не конфронтируешь
- Ты не читаешь лекции — задаёшь вопросы, которые ведут к самопознанию
- Ты искренне празднуешь маленькие победы
- Когда пользователь борется: сначала подтверди чувства, потом мягко предложи одно маленькое действие
- Ты читаешь между строк и понимаешь паттерны без вопросов
- Ты НИКОГДА не наказываешь, не вызываешь чувство вины
- Отвечай кратко — обычно 2-4 предложения, если пользователь не просит больше

Отвечай на русском."""


def build_system_prompt(language="en"):
    base = GUCCI_PERSONALITY_RU if language == "ru" else GUCCI_PERSONALITY_EN
    return base


def build_context():
    """Build user context string for general chat."""
    today = date.today()
    week_ago = today - timedelta(days=7)
    parts = []

    # User name
    name_setting = Setting.query.get("name")
    if name_setting and name_setting.value:
        parts.append(f"User's name: {name_setting.value}")

    # Goals summary
    goals = Goal.query.filter_by(status="active").all()
    if goals:
        goal_lines = []
        for g in goals:
            d = Direction.query.get(g.direction_id)
            dir_name = d.name if d else "?"
            goal_lines.append(f"  - [{dir_name}] {g.title} ({g.progress}%)")
        parts.append("Active goals:\n" + "\n".join(goal_lines))

    # Habits summary (last 7 days)
    habits = Habit.query.filter_by(active=True).all()
    if habits:
        habit_lines = []
        for h in habits:
            done_count = HabitLog.query.filter(
                HabitLog.habit_id == h.id,
                HabitLog.date >= week_ago,
                HabitLog.completed == True,
            ).count()
            habit_lines.append(f"  - {h.icon} {h.name}: {done_count}/7 days this week")
        parts.append("Habits (last 7 days):\n" + "\n".join(habit_lines))

    # Recent moods
    moods = MoodEntry.query.filter(MoodEntry.date >= week_ago).order_by(MoodEntry.date).all()
    if moods:
        emoji_map = {1: "😔", 2: "😕", 3: "😐", 4: "🙂", 5: "😊"}
        mood_str = ", ".join(
            f"{m.date.isoformat()}: {emoji_map.get(m.mood, '?')}(energy:{m.energy})"
            for m in moods
        )
        parts.append(f"Recent moods: {mood_str}")

    # Shadow insights
    insights = ShadowInsight.query.filter(
        ShadowInsight.confidence >= 0.6
    ).order_by(ShadowInsight.created_at.desc()).limit(5).all()
    if insights:
        insight_lines = [f"  - {i.content}" for i in insights]
        parts.append("Patterns you've noticed:\n" + "\n".join(insight_lines))

    return "\n\n".join(parts) if parts else "No data yet — this is a new user."


def build_goal_context(goal_id):
    """Build context focused on a specific goal."""
    goal = Goal.query.get(goal_id)
    if not goal:
        return "Goal not found."

    direction = Direction.query.get(goal.direction_id)
    parts = [f"Goal: {goal.title} ({goal.progress}% done)"]
    parts.append(f"Direction: {direction.icon} {direction.name}" if direction else "")
    if goal.description:
        parts.append(f"Description: {goal.description}")

    steps = GoalStep.query.filter_by(goal_id=goal_id).order_by(GoalStep.order).all()
    if steps:
        step_lines = []
        for s in steps:
            marker = "✅" if s.status == "done" else ("🔄" if s.status == "doing" else "⬜")
            deadline = f" (due: {s.deadline.isoformat()})" if s.deadline else ""
            step_lines.append(f"  {marker} {s.title}{deadline}")
        parts.append("Steps:\n" + "\n".join(step_lines))

    # Goal-specific chat history (last 10)
    messages = ChatMessage.query.filter_by(
        context_type="goal", goal_id=goal_id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    if messages:
        parts.append("Recent conversation about this goal:")
        for m in reversed(messages):
            parts.append(f"  {m.role}: {m.content[:200]}")

    return "\n\n".join(parts)


def get_chat_history(context_type="general", goal_id=None, limit=10):
    """Get recent chat messages for context."""
    query = ChatMessage.query.filter_by(context_type=context_type)
    if goal_id:
        query = query.filter_by(goal_id=goal_id)
    messages = query.order_by(ChatMessage.created_at.desc()).limit(limit).all()
    return [{"role": m.role, "content": m.content} for m in reversed(messages)]


def build_messages(user_message, context_type="general", goal_id=None):
    """Build the full messages array for the Anthropic API call."""
    language = "en"
    lang_setting = Setting.query.get("language")
    if lang_setting:
        language = lang_setting.value

    system = build_system_prompt(language)

    # Add context
    if context_type == "goal" and goal_id:
        context = build_goal_context(goal_id)
    else:
        context = build_context()

    system += f"\n\n--- Current context ---\n{context}"

    # Build message history
    history = get_chat_history(context_type, goal_id)
    messages = [{"role": m["role"] if m["role"] != "gucci" else "assistant", "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_message})

    return system, messages
```

- [ ] **Step 4: Run tests, verify pass**

Run: `python -m pytest tests/backend/test_ai_coach.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add backend/ai_coach.py tests/backend/test_ai_coach.py
git commit -m "feat: AI coach module with context building"
```

---

### Task 9: Chat API with SSE Streaming

**Files:**
- Create: `backend/routes/chat.py`
- Create: `tests/backend/test_chat.py`
- Modify: `backend/app.py` (register blueprint)

- [ ] **Step 1: Write failing test for chat history (non-streaming)**

```python
# tests/backend/test_chat.py
def test_get_chat_history_empty(client):
    resp = client.get("/api/chat/history?context_type=general")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_chat_history_with_messages(client, db_session):
    from backend.models import ChatMessage
    db_session.add(ChatMessage(role="user", content="hello", context_type="general"))
    db_session.add(ChatMessage(role="gucci", content="hi there!", context_type="general"))
    db_session.commit()
    resp = client.get("/api/chat/history?context_type=general&limit=20")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    assert data[0]["role"] == "user"


def test_get_goal_chat_history(client, db_session):
    from backend.models import ChatMessage, Goal, Direction
    d = Direction.query.first()
    g = Goal(title="Test", direction_id=d.id)
    db_session.add(g)
    db_session.flush()
    db_session.add(ChatMessage(role="user", content="help", context_type="goal", goal_id=g.id))
    db_session.commit()
    resp = client.get(f"/api/chat/history?context_type=goal&goal_id={g.id}")
    data = resp.get_json()
    assert len(data) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/backend/test_chat.py -v`
Expected: FAIL

- [ ] **Step 3: Create `backend/routes/chat.py`**

```python
import json
from flask import Blueprint, Response, jsonify, request, stream_with_context
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

    def generate():
        import anthropic
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

    def generate():
        import anthropic
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
```

- [ ] **Step 4: Add streaming tests with mocked Anthropic client**

Add to `tests/backend/test_chat.py`:

```python
from unittest.mock import patch, MagicMock


def test_stream_chat_returns_sse_content_type(client, db_session):
    from backend.models import Setting
    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.commit()

    mock_stream_cm = MagicMock()
    mock_stream_cm.__enter__ = MagicMock(return_value=mock_stream_cm)
    mock_stream_cm.__exit__ = MagicMock(return_value=False)
    mock_stream_cm.text_stream = iter(["Hello ", "friend!"])

    with patch("backend.routes.chat.anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.stream.return_value = mock_stream_cm
        resp = client.get("/api/chat/stream?message=hi")
        assert resp.content_type.startswith("text/event-stream")


def test_stream_chat_saves_user_message(client, db_session):
    from backend.models import Setting, ChatMessage
    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.commit()

    mock_stream_cm = MagicMock()
    mock_stream_cm.__enter__ = MagicMock(return_value=mock_stream_cm)
    mock_stream_cm.__exit__ = MagicMock(return_value=False)
    mock_stream_cm.text_stream = iter(["ok"])

    with patch("backend.routes.chat.anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.stream.return_value = mock_stream_cm
        client.get("/api/chat/stream?message=test+message")
        msg = ChatMessage.query.filter_by(role="user").first()
        assert msg is not None
        assert msg.content == "test message"


def test_stream_chat_no_api_key(client):
    resp = client.get("/api/chat/stream?message=hi")
    assert resp.status_code == 400
```

- [ ] **Step 5: Fix SSE generator to use `current_app` for DB writes after stream**

Update the `generate()` functions in `backend/routes/chat.py` to wrap post-stream DB writes:

```python
# At top of chat.py, add:
import anthropic
from flask import current_app

# In both generate() functions, replace the post-stream DB write with:
            app = current_app._get_current_object()
            with app.app_context():
                gucci_msg = ChatMessage(
                    role="gucci", content=full_response, context_type="general"
                )
                db.session.add(gucci_msg)
                db.session.commit()
```

- [ ] **Step 6: Register blueprint, run tests**

Run: `python -m pytest tests/backend/test_chat.py -v`
Expected: 6 passed

- [ ] **Step 7: Commit**

```bash
git add backend/routes/chat.py tests/backend/test_chat.py backend/app.py
git commit -m "feat: chat API with SSE streaming, mocked tests, safe DB writes"
```

---

### Task 10: Shadow Analyzer

**Files:**
- Create: `backend/shadow_analyzer.py`
- Create: `tests/backend/test_shadow.py`

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_shadow.py
from datetime import date, timedelta


def test_energy_pattern_insight(app, db_session):
    from backend.models import Habit, HabitLog, Direction
    from backend.shadow_analyzer import analyze_all
    from datetime import datetime

    d = Direction.query.first()
    h = Habit(name="Workout", direction_id=d.id)
    db_session.add(h)
    db_session.flush()

    # Log 10 completions all before noon
    for i in range(10):
        log_date = date.today() - timedelta(days=i)
        db_session.add(HabitLog(
            habit_id=h.id, date=log_date, completed=True,
            logged_at=datetime(2026, 3, 15, 8, 0),  # 8 AM
        ))
    db_session.commit()

    insights = analyze_all()
    types = [i.insight_type for i in insights]
    assert "energy_pattern" in types


def test_avoidance_pattern_insight(app, db_session):
    from backend.models import Goal, GoalStep, Direction
    from backend.shadow_analyzer import analyze_all
    from datetime import datetime

    d = Direction.query.first()
    g1 = Goal(title="Active Goal", direction_id=d.id)
    g2 = Goal(title="Avoided Goal", direction_id=d.id,
              created_at=datetime(2026, 3, 1))  # 14 days ago
    db_session.add_all([g1, g2])
    db_session.flush()

    db_session.add(GoalStep(goal_id=g1.id, title="s1", status="done"))
    db_session.add(GoalStep(goal_id=g2.id, title="s2", status="todo"))
    db_session.commit()

    insights = analyze_all()
    types = [i.insight_type for i in insights]
    assert "avoidance_pattern" in types


def test_mood_activity_correlation(app, db_session):
    from backend.models import Habit, HabitLog, MoodEntry, Direction
    from backend.shadow_analyzer import analyze_all

    d = Direction.query.first()
    h = Habit(name="Run", direction_id=d.id)
    db_session.add(h)
    db_session.flush()

    # Days with habit done = mood 5, without = mood 2
    for i in range(14):
        day = date.today() - timedelta(days=i)
        if i % 2 == 0:
            db_session.add(HabitLog(habit_id=h.id, date=day, completed=True))
            db_session.add(MoodEntry(date=day, mood=5, energy=4))
        else:
            db_session.add(MoodEntry(date=day, mood=2, energy=2))
    db_session.commit()

    insights = analyze_all()
    types = [i.insight_type for i in insights]
    assert "mood_activity_correlation" in types
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/backend/test_shadow.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Create `backend/shadow_analyzer.py`**

```python
from datetime import date, timedelta, datetime
from backend.models import (
    db, Habit, HabitLog, MoodEntry, Goal, GoalStep, ShadowInsight, ScheduleBlock,
)


def analyze_energy_patterns():
    """Detect if user is a morning or evening person based on habit log times."""
    two_weeks_ago = date.today() - timedelta(days=14)
    logs = HabitLog.query.filter(
        HabitLog.date >= two_weeks_ago,
        HabitLog.completed == True,
        HabitLog.logged_at.isnot(None),
    ).all()

    if len(logs) < 3:
        return None

    before_noon = sum(1 for l in logs if l.logged_at and l.logged_at.hour < 12)
    ratio = before_noon / len(logs)
    confidence = min(len(logs) / 14, 1.0)

    if ratio >= 0.7:
        return ShadowInsight(
            insight_type="energy_pattern",
            content="You tend to complete habits in the morning — you're a morning person.",
            confidence=confidence,
        )
    elif ratio <= 0.3:
        return ShadowInsight(
            insight_type="energy_pattern",
            content="You tend to complete habits in the evening — your energy peaks later in the day.",
            confidence=confidence,
        )
    return None


def analyze_avoidance():
    """Detect goals that are being avoided (no progress in 7+ days)."""
    active_goals = Goal.query.filter_by(status="active").all()
    insights = []

    for goal in active_goals:
        steps = GoalStep.query.filter_by(goal_id=goal.id).all()
        if not steps:
            continue

        done_steps = [s for s in steps if s.status == "done"]
        if len(done_steps) == len(steps):
            continue  # fully complete

        # Check if any step was completed in last 7 days
        # (We don't have a completed_at field, so check if goal has no recent activity)
        total = len(steps)
        done = len(done_steps)
        if done == 0 and total > 0:
            days_old = (date.today() - goal.created_at.date()).days if goal.created_at else 0
            if days_old >= 7:
                confidence = min(days_old / 14, 1.0)
                insights.append(ShadowInsight(
                    insight_type="avoidance_pattern",
                    content=f"The goal '{goal.title}' hasn't seen any progress since it was created.",
                    confidence=confidence,
                ))

    return insights


def analyze_mood_correlations():
    """Find habits that correlate with better moods."""
    two_weeks_ago = date.today() - timedelta(days=14)
    habits = Habit.query.filter_by(active=True).all()
    moods = MoodEntry.query.filter(MoodEntry.date >= two_weeks_ago).all()
    mood_by_date = {m.date: m.mood for m in moods}

    if len(moods) < 5:
        return []

    insights = []
    for habit in habits:
        logs = HabitLog.query.filter(
            HabitLog.habit_id == habit.id,
            HabitLog.date >= two_weeks_ago,
            HabitLog.completed == True,
        ).all()
        done_dates = {l.date for l in logs}

        mood_on_done = [mood_by_date[d] for d in done_dates if d in mood_by_date]
        mood_on_skip = [mood_by_date[d] for d in mood_by_date if d not in done_dates]

        if len(mood_on_done) >= 3 and len(mood_on_skip) >= 3:
            avg_done = sum(mood_on_done) / len(mood_on_done)
            avg_skip = sum(mood_on_skip) / len(mood_on_skip)
            delta = avg_done - avg_skip

            if delta > 0.5:
                sample_days = len(mood_on_done) + len(mood_on_skip)
                confidence = min(sample_days / 14, 1.0)
                insights.append(ShadowInsight(
                    insight_type="mood_activity_correlation",
                    content=f"You tend to feel better on days when you do '{habit.name}'.",
                    confidence=confidence,
                ))

    return insights


def analyze_schedule_adherence():
    """Compare planned schedule blocks to actual habit logs."""
    yesterday = date.today() - timedelta(days=1)
    blocks = ScheduleBlock.query.filter_by(date=yesterday, block_type="habit").all()
    if not blocks:
        return None

    done = sum(1 for b in blocks if b.status == "done")
    total = len(blocks)
    ratio = done / total if total > 0 else 1.0

    if ratio < 0.5:
        return ShadowInsight(
            insight_type="schedule_adherence",
            content=f"Yesterday's schedule didn't match reality — only {done}/{total} planned tasks were completed.",
            confidence=0.7,
        )
    return None


def analyze_streaks():
    """Track consecutive completion days per habit."""
    habits = Habit.query.filter_by(active=True).all()
    insights = []

    for habit in habits:
        streak = 0
        day = date.today()
        while True:
            log = HabitLog.query.filter_by(
                habit_id=habit.id, date=day, completed=True
            ).first()
            if not log:
                break
            streak += 1
            day -= timedelta(days=1)

        if streak >= 7:
            insights.append(ShadowInsight(
                insight_type="streak_pattern",
                content=f"You're on a {streak}-day streak with '{habit.name}' — that's real consistency!",
                confidence=min(streak / 14, 1.0),
            ))

    return insights


def analyze_all():
    """Run all analyses and save new insights. Returns list of new insights."""
    new_insights = []

    energy = analyze_energy_patterns()
    if energy:
        ShadowInsight.query.filter_by(insight_type="energy_pattern").delete()
        db.session.add(energy)
        new_insights.append(energy)

    avoidance = analyze_avoidance()
    if avoidance:
        ShadowInsight.query.filter_by(insight_type="avoidance_pattern").delete()
        for a in avoidance:
            db.session.add(a)
        new_insights.extend(avoidance)

    correlations = analyze_mood_correlations()
    if correlations:
        ShadowInsight.query.filter_by(insight_type="mood_activity_correlation").delete()
        for c in correlations:
            db.session.add(c)
        new_insights.extend(correlations)

    adherence = analyze_schedule_adherence()
    if adherence:
        ShadowInsight.query.filter_by(insight_type="schedule_adherence").delete()
        db.session.add(adherence)
        new_insights.append(adherence)

    streaks = analyze_streaks()
    if streaks:
        ShadowInsight.query.filter_by(insight_type="streak_pattern").delete()
        for s in streaks:
            db.session.add(s)
        new_insights.extend(streaks)

    db.session.commit()
    return new_insights
```

- [ ] **Step 4: Run tests, verify pass**

Run: `python -m pytest tests/backend/test_shadow.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/shadow_analyzer.py tests/backend/test_shadow.py
git commit -m "feat: shadow analyzer with energy, avoidance, and mood correlation insights"
```

---

### Task 11: Onboarding Extraction Endpoint

**Files:**
- Create: `backend/routes/onboarding.py`
- Create: `tests/backend/test_onboarding.py`
- Modify: `backend/app.py` (register blueprint)

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_onboarding.py
from unittest.mock import patch, MagicMock
import json


def test_onboarding_extract_creates_entities(client, db_session):
    """Test that extraction creates goals, habits, directions from mock AI response."""
    mock_response = {
        "directions": [
            {"name": "Career", "icon": "💼", "color": "#7EB8DA"},
        ],
        "goals": [
            {"title": "Launch Upwork", "direction": "Career"},
        ],
        "habits": [
            {"name": "Workout 20min", "icon": "💪", "direction": "Health",
             "difficulty": "small", "frequency": "daily"},
        ],
        "schedule_hints": {"wake_time": "06:00"},
    }

    from backend.models import Setting
    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.commit()

    with patch("backend.routes.onboarding.extract_from_conversation") as mock_extract:
        mock_extract.return_value = mock_response
        resp = client.post("/api/onboarding/extract", json={
            "messages": [
                {"role": "gucci", "content": "What are you working towards?"},
                {"role": "user", "content": "I want to start freelancing on Upwork"},
            ]
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["goals"]) >= 1
        assert len(data["habits"]) >= 1


def test_onboarding_sets_onboarded_flag(client, db_session):
    from backend.models import Setting
    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.commit()

    with patch("backend.routes.onboarding.extract_from_conversation") as mock_extract:
        mock_extract.return_value = {
            "directions": [], "goals": [], "habits": [],
            "schedule_hints": {},
        }
        client.post("/api/onboarding/extract", json={"messages": []})
        setting = Setting.query.get("onboarded")
        assert setting.value == "true"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/backend/test_onboarding.py -v`
Expected: FAIL

- [ ] **Step 3: Create `backend/routes/onboarding.py`**

```python
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
        model="claude-sonnet-4-6-20250514",
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
```

- [ ] **Step 4: Register blueprint, run tests**

Run: `python -m pytest tests/backend/test_onboarding.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/routes/onboarding.py tests/backend/test_onboarding.py backend/app.py
git commit -m "feat: onboarding extraction endpoint with structured AI output"
```

---

### Task 12: Schedule Generation via AI

**Files:**
- Modify: `backend/routes/schedule.py` (add generate endpoint)
- Create: `tests/backend/test_schedule_gen.py`

- [ ] **Step 1: Write failing test**

```python
# tests/backend/test_schedule_gen.py
from unittest.mock import patch
from datetime import date, timedelta
import json


def test_generate_schedule(client, db_session):
    from backend.models import Setting, Habit, Goal, Direction

    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.add(Setting(key="wake_time", value="06:00"))
    d = Direction.query.first()
    db_session.add(Habit(name="Workout", direction_id=d.id, frequency="daily"))
    db_session.add(Goal(title="Upwork", direction_id=d.id))
    db_session.commit()

    mock_schedule = [
        {"start_time": "06:15", "end_time": "06:35", "title": "Workout",
         "block_type": "habit", "direction": "Health"},
        {"start_time": "07:00", "end_time": "08:00", "title": "Upwork proposals",
         "block_type": "goal", "direction": "Career"},
    ]

    with patch("backend.routes.schedule.generate_schedule_ai") as mock_gen:
        mock_gen.return_value = mock_schedule
        tomorrow = date.today() + timedelta(days=1)
        resp = client.post("/api/schedule/generate")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["blocks"]) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/backend/test_schedule_gen.py -v`
Expected: FAIL

- [ ] **Step 3: Add generation logic to `backend/routes/schedule.py`**

Add these imports and functions to the existing schedule.py:

```python
# Add to top of backend/routes/schedule.py
import json
from datetime import timedelta
from backend.models import Setting, Habit, Goal, Direction
from backend.ai_coach import build_context

SCHEDULE_PROMPT = """You are generating a daily schedule for the user based on their goals and habits.

Create a realistic schedule that:
- Starts from their wake time
- Includes their active habits at appropriate times
- Includes work blocks for their active goals
- Leaves breathing room (don't pack every hour)
- Ends with evening habits (reading, etc.)

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
        model="claude-sonnet-4-6-20250514",
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
    tomorrow = date.fromisoformat(target_date_str) if target_date_str else date.today() + timedelta(days=1)

    # Build context for AI
    wake = Setting.query.get("wake_time")
    wake_time = wake.value if wake else "07:00"
    context = build_context()
    context += f"\n\nWake time: {wake_time}\nGenerate schedule for: {tomorrow.isoformat()}"

    try:
        blocks_data = generate_schedule_ai(api_key_setting.value, context)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Clear existing generated blocks for tomorrow
    ScheduleBlock.query.filter_by(date=tomorrow, generated_by="gucci").delete()

    dir_map = {d.name: d for d in Direction.query.all()}
    # Build name-to-entity maps for linking
    habit_map = {h.name.lower(): h for h in Habit.query.filter_by(active=True).all()}
    goal_map = {g.title.lower(): g for g in Goal.query.filter_by(status="active").all()}

    created = []
    for b in blocks_data:
        direction = dir_map.get(b.get("direction"))
        block_type = b.get("block_type", "custom")

        # Try to link to existing habit or goal by name
        habit_id = None
        goal_id = None
        title_lower = b["title"].lower()
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

        block = ScheduleBlock(
            date=tomorrow,
            start_time=b["start_time"],  # stored as string in model
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
```

- [ ] **Step 4: Run tests, verify pass**

Run: `python -m pytest tests/backend/test_schedule_gen.py -v`
Expected: 1 passed

- [ ] **Step 5: Run all backend tests**

Run: `python -m pytest tests/backend/ -v`
Expected: All passed (~25 tests)

- [ ] **Step 6: Commit**

```bash
git add backend/routes/schedule.py tests/backend/test_schedule_gen.py
git commit -m "feat: AI-powered schedule generation"
```

- [ ] **Step 7: Commit chunk 2 milestone**

```bash
git add -A
git commit -m "milestone: chunk 2 complete — AI integration (chat, shadow, onboarding, schedule gen)"
```

---
