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
