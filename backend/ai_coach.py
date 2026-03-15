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

ONBOARDING_EN = """
IMPORTANT — NEW user. Get to know them through SHORT natural conversation (3-4 exchanges max), then set up their app.

CONVERSATION FLOW (keep it tight):
1. First message: warm greeting + ask their name and what brought them here (ONE message, TWO things)
2. After they respond: reflect what you heard, ask what specific habits or routines they want to build
3. After they respond: ask about their daily schedule (when they wake, when they have energy)
4. Summarize and offer to set things up

KEY RULES:
- Keep YOUR messages to 2-3 sentences. Don't ramble.
- Don't ask about mood, hobbies, what brings them joy — that's not needed for setup
- Don't explore feelings or go deep — this is PRACTICAL info gathering
- When you have enough (name + goals + habits + wake time), say EXACTLY this phrase:
  "SETUP_READY: [summary of what you learned]"
  This triggers the app to create their goals and habits automatically.

Example final message:
"Отлично! Я всё понял — ты хочешь наладить фриланс, делать зарядку по утрам и читать перед сном. Просыпаешься около 7. Давай я всё настрою! SETUP_READY: name=Миша, goals=[фриланс на Upwork, портфолио QA], habits=[зарядка 20мин, чтение 20 страниц, фокус-блок 1ч], wake=07:00"

The SETUP_READY line MUST be at the very end of your message and follow the exact format above."""

ONBOARDING_RU = """
ВАЖНО — НОВЫЙ пользователь. Познакомься через КОРОТКИЙ естественный разговор (3-4 обмена максимум), потом настрой приложение.

ПОРЯДОК РАЗГОВОРА (держи коротко):
1. Первое сообщение: тёплое приветствие + спроси имя и что привело сюда (ОДНО сообщение, ДВЕ вещи)
2. После ответа: отрази что услышал, спроси какие конкретно привычки или рутины хочет наладить
3. После ответа: спроси про расписание (когда встаёт, когда энергия)
4. Подведи итог и предложи настроить

КЛЮЧЕВЫЕ ПРАВИЛА:
- Твои сообщения — 2-3 предложения. Не разливайся.
- Не спрашивай про настроение, хобби, что приносит радость — это не нужно для настройки
- Не углубляйся в чувства — это ПРАКТИЧЕСКИЙ сбор информации
- Когда достаточно инфы (имя + цели + привычки + время подъёма), напиши ТОЧНО эту фразу:
  "SETUP_READY: [итог того что узнал]"
  Это запускает автоматическое создание целей и привычек.

Пример финального сообщения:
"Отлично! Я всё понял — ты хочешь наладить фриланс, делать зарядку по утрам и читать перед сном. Просыпаешься около 7. Давай я всё настрою! SETUP_READY: name=Миша, goals=[фриланс на Upwork, портфолио QA], habits=[зарядка 20мин, чтение 20 страниц, фокус-блок 1ч], wake=07:00"

Строка SETUP_READY ОБЯЗАТЕЛЬНО должна быть в самом конце сообщения и следовать точному формату выше."""


GOAL_CHAT_EN = """
You are a sub-agent focused on ONE specific goal. You already know the user from the main Gucci conversations — don't re-ask about mood, energy, hobbies, or general life. Stay on topic.

Rules:
- You know the goal details, steps, and progress from the context below. Use this info.
- Start with a brief, warm observation about the goal status ("I see you've done step 1 already, nice!")
- Ask ONE focused question about the goal: what's blocking them, what's the next move, do they need help breaking something down
- If the user asks for help planning — give concrete, actionable steps (2-3 max)
- If the user just wants to discuss — listen and reflect, keep it short
- Do NOT ask about unrelated topics (mood, energy, other goals, hobbies)
- Conversation should naturally end in 3-5 exchanges. Don't drag it out.
- When the conversation reaches a natural conclusion, say something like "Sounds like a plan! Mark the step done when you're ready ✓"
- Keep responses to 2-3 sentences max"""

GOAL_CHAT_RU = """
Ты суб-агент, сфокусированный на ОДНОЙ конкретной цели. Ты уже знаешь пользователя из основных разговоров с Gucci — не спрашивай заново про настроение, энергию, хобби или жизнь в целом. Держись темы.

Правила:
- Ты знаешь детали цели, шаги и прогресс из контекста ниже. Используй эту информацию.
- Начни с короткого, тёплого наблюдения о статусе цели ("Вижу, первый шаг уже сделан, круто!")
- Задай ОДИН конкретный вопрос о цели: что мешает, какой следующий шаг, нужна ли помощь разбить задачу
- Если просят помочь спланировать — дай конкретные шаги (2-3 максимум)
- Если просто хотят обсудить — слушай и отражай, коротко
- НЕ спрашивай на посторонние темы (настроение, энергия, другие цели, хобби)
- Разговор должен естественно завершиться за 3-5 обменов. Не затягивай.
- Когда разговор подошёл к концу, скажи что-то вроде "Звучит как план! Отметь шаг выполненным, когда будешь готов ✓"
- Отвечай максимум 2-3 предложениями"""


def build_system_prompt(language="en", context_type="general"):
    base = GUCCI_PERSONALITY_RU if language == "ru" else GUCCI_PERSONALITY_EN

    if context_type == "goal":
        goal_prompt = GOAL_CHAT_RU if language == "ru" else GOAL_CHAT_EN
        base += "\n" + goal_prompt
    else:
        # Check if user is onboarded
        onboarded = Setting.query.get("onboarded")
        is_new = not onboarded or onboarded.value != "true"

        if is_new:
            onboarding = ONBOARDING_RU if language == "ru" else ONBOARDING_EN
            base += "\n" + onboarding

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

    system = build_system_prompt(language, context_type)

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
