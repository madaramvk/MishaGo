# MishaGo — Design Specification

**Date**: 2026-03-15
**Status**: Draft
**Location**: `D:\Pet-projects\MishaGo\`

---

## 1. Vision

MishaGo is a personal wellness & goal organizer built as a PWA (Progressive Web App) for Android. At its center is **Gucci** — a mystical spirit companion (rabbit-cat hybrid with spiritual aura) who lives in a Japanese zen greenhouse garden. Gucci is the face of the app, the main AI agent, and the user's thinking partner.

The app helps users build positive life patterns (workout, reading, focus, career work) through **gentle behavioral activation** — no punishment, no guilt, no streak resets. Gucci earns the user's trust through natural conversation, shadow-analyzes behavioral patterns, and guides goal achievement with psychological awareness.

### Core Principles

1. **Gucci IS the app** — not a feature, not a pet to grow. The main interface and intelligence.
2. **No punishment** — XP never decreases, garden never dies, only pauses growing.
3. **Action before motivation** — behavioral activation: doing creates motivation, not the other way around.
4. **Fast & simple** — daily check-in under 30 seconds. Depth is optional.
5. **Shadow analysis** — Gucci reads between the lines, doesn't interrogate. Extracts insights naturally through friendly conversation.
6. **Goal-driven schedule** — daily time management is generated from user's actual goals, not arbitrary blocks.

---

## 2. Target User

- Person struggling with self-discipline during a life transition
- Needs structure but traditional systems feel rigid/punishing
- May have depression, ADHD traits, or executive dysfunction
- Wants a thinking partner, not a task manager
- Has career + life goals that need daily actionable breakdown
- Uses Android phone as primary device

---

## 3. Technical Architecture

### Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) — REST API + Server-Sent Events (SSE) for chat streaming |
| Frontend | React (Vite) — PWA with service worker |
| Database | SQLite (single file) |
| AI | Claude Sonnet 4.6 API (companion chat, coaching, schedule generation) |
| Animations | CSS transitions + Lottie (pet, garden) |
| Notifications | Web Push API (smart, deadline-driven) |

### Project Structure

```
MishaGo/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── models.py               # SQLAlchemy models
│   ├── routes/
│   │   ├── habits.py           # Habit CRUD + daily logs
│   │   ├── goals.py            # Goals, directions, steps
│   │   ├── mood.py             # Mood entries
│   │   ├── pet.py              # Gucci state, garden level
│   │   ├── chat.py             # AI chat (general + per-goal)
│   │   └── schedule.py         # AI-generated daily schedule
│   ├── ai_coach.py             # Claude Haiku integration
│   ├── shadow_analyzer.py      # Background pattern analysis
│   └── config.py               # Settings, API keys
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── GucciHome.jsx   # Main page — Gucci + greenhouse
│   │   │   ├── Goals.jsx       # Goals by direction + daily board
│   │   │   ├── DayCanvas.jsx   # Flowing time canvas
│   │   │   └── Me.jsx          # Stats, settings
│   │   ├── components/
│   │   │   ├── Gucci.jsx       # Animated companion
│   │   │   ├── Garden.jsx      # Zen greenhouse background
│   │   │   ├── MoodPicker.jsx  # Emoji mood bubbles
│   │   │   ├── HabitCard.jsx   # Tap-to-check habit
│   │   │   ├── GoalCard.jsx    # Goal bubble with progress
│   │   │   ├── GoalChat.jsx    # Per-goal sub-agent chat
│   │   │   ├── TimeBubble.jsx  # Task bubble on day canvas
│   │   │   ├── BubblePopup.jsx # Expanded task popup
│   │   │   ├── ChatBubble.jsx  # Chat message bubble
│   │   │   └── NavBar.jsx      # Bottom 4-tab navigation
│   │   ├── themes/
│   │   │   ├── light.css       # Warm cream theme
│   │   │   └── dark.css        # Deep plum theme
│   │   ├── hooks/
│   │   │   ├── useChat.js      # Chat state + streaming
│   │   │   └── useSchedule.js  # Schedule generation
│   │   ├── sw.js               # Service worker
│   │   └── App.jsx             # Router + theme provider
│   ├── public/
│   │   ├── manifest.json       # PWA manifest
│   │   └── assets/
│   │       ├── gucci/          # Gucci animations (Lottie)
│   │       └── garden/         # Garden elements (SVG/Lottie)
│   └── index.html
├── tests/
│   ├── backend/
│   └── frontend/
├── requirements.txt
├── package.json
└── mishago.db
```

### Data Flow

```
User taps habit ✓
  → React POST /api/habits/log
  → Flask saves to SQLite
  → shadow_analyzer updates pattern data (rule-based, no API call)
  → returns updated Gucci mood
  → React animates Gucci reaction

User chats with Gucci
  → React GET /api/chat/stream?message=... (SSE endpoint)
  → Flask builds context (goals, moods, habits, patterns)
  → sends to Claude Sonnet with system prompt
  → streams response back via SSE (text/event-stream)
  → on stream complete: saves full message to chat history
  → shadow_analyzer extracts insights silently (rule-based)

User taps goal → sub-agent chat
  → React GET /api/chat/goal/{goal_id}/stream?message=... (SSE)
  → Flask builds goal-specific context
  → sends to Sonnet with goal-focused system prompt
  → streams response via SSE
  → saves to goal chat history
```

### Deployment Model

Backend runs **locally only** (localhost). The API key is stored in SQLite settings and never leaves the machine except in direct Anthropic API calls. There is no remote server.

### API Endpoints

```
# Habits
POST   /api/habits              — Create habit
GET    /api/habits              — List active habits
PUT    /api/habits/<id>         — Update habit
POST   /api/habits/log          — Log habit completion {habit_id, date, completed, energy_level?}
GET    /api/habits/log/<date>   — Get logs for a date

# Goals & Directions
GET    /api/directions          — List directions
POST   /api/directions          — Create direction
GET    /api/goals               — List goals (filter by direction_id, status)
POST   /api/goals               — Create goal
PUT    /api/goals/<id>          — Update goal
GET    /api/goals/<id>/steps    — List steps for goal
POST   /api/goals/<id>/steps   — Create step
PUT    /api/goals/<id>/steps/<step_id> — Update step status

# Mood
POST   /api/mood                — Log mood {mood (1-5), energy (1-5), note?}
GET    /api/mood?days=7         — Get recent moods

# Pet
GET    /api/pet                 — Get Gucci state (mood, xp, garden_stage, aura)

# Chat (SSE streaming)
GET    /api/chat/stream?message=<text>              — General chat with Gucci
GET    /api/chat/goal/<goal_id>/stream?message=<text> — Goal-specific chat
GET    /api/chat/history?context_type=general&limit=20 — Chat history
GET    /api/chat/history?context_type=goal&goal_id=<id>&limit=20

# Schedule
GET    /api/schedule/<date>     — Get schedule for date
POST   /api/schedule/generate   — Ask Gucci to generate tomorrow's schedule
PUT    /api/schedule/<id>       — Update block (mark done/skipped, edit times)
POST   /api/schedule            — Manually add block

# Settings
GET    /api/settings            — Get user settings
PUT    /api/settings            — Update settings (theme, language, api_key, wake_time, etc.)

# Onboarding
POST   /api/onboarding/extract  — Structured extraction from chat (creates directions, goals, habits)
```

---

## 4. Data Model

Single-user app — no `user_id` foreign keys needed. User settings stored in a `Settings` key-value table.

### Settings (key-value store)

| Key | Type | Description |
|---|---|---|
| name | string | User's name |
| language | string | "ru" / "en" |
| theme | string | "light" / "dark" |
| wake_time | string | e.g., "06:00" |
| api_key | string | Claude API key (encrypted at rest) |
| notification_prefs | json | When/how to notify |
| onboarded | bool | Whether onboarding is complete |
| created_at | datetime | First launch |

### Pet (Gucci)

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| name | string | Always "Gucci" |
| mood | enum | content / happy / cozy / sleepy / concerned |
| xp | int | Only increases, never decreases |
| aura_color | string | Shifts based on consistency |
| garden_stage | int | 0-9, evolves at XP thresholds |
| accessories | json | Unlocked items (earned via milestones) |

**Gucci mood** is calculated from the last 3 days:
- 3+ habits done today → happy
- Chatted today → content
- Nothing logged for 2 days → sleepy
- Nothing for 3+ days → concerned (not angry, not punishing — just worried)

**Garden stages**: bare earth → moss → small stones → bamboo sprout → zen stones arrangement → ferns → bonsai → water feature → flowering → full greenhouse with fireflies

**XP thresholds**: 0, 50, 150, 300, 500, 800, 1200, 1800, 2500, 3500

### Direction

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| name | string | e.g., "Career", "Health", "Mind" |
| icon | string | Emoji |
| color | string | Hex color for bubbles |

Default directions:
- 💼 Career — `#7EB8DA` (soft blue)
- 💪 Health — `#9DD6A3` (sage green)
- 📚 Mind — `#C4A8E0` (lavender)
- 🌱 Life — `#F0C987` (warm amber)

User can add custom directions.

**Seeding**: The 4 default directions are created on first app launch (before onboarding). Onboarding may add more or rename them based on conversation.

### Goal

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| direction_id | int | FK to Direction |
| title | string | Goal name |
| description | text | Details |
| status | enum | active / paused / done |
| progress | int | 0-100% |
| created_by | enum | user / gucci |
| created_at | datetime | |

### GoalStep

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| goal_id | int | FK to Goal |
| title | string | Step name |
| status | enum | todo / doing / done |
| deadline | date | Optional due date (enables notifications) |
| created_by | enum | user / gucci |
| order | int | Sort order |

**Goal progress** is auto-calculated: `completed steps / total steps * 100`. Updated whenever a step status changes.

### Habit

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| direction_id | int | FK to Direction |
| name | string | e.g., "Workout 20min" |
| icon | string | Emoji |
| difficulty | enum | tiny / small / medium |
| xp_reward | int | Based on difficulty: 3 / 5 / 10 |
| frequency | enum | daily / weekdays / weekends / custom |
| custom_days | string | Comma-separated day numbers (0=Mon..6=Sun), used when frequency=custom |
| active | bool | Can be paused |

**Today's habits** are filtered by frequency: `daily` shows every day, `weekdays` Mon-Fri, `weekends` Sat-Sun, `custom` checks `custom_days` against current day of week.

### HabitLog

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| habit_id | int | FK to Habit |
| date | date | Which day |
| completed | bool | Done or not |
| energy_level | enum | low / medium / high (optional) |
| logged_at | datetime | When the user checked it |

### MoodEntry

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| date | date | Which day |
| mood | int | 1-5 mapped to: 1=😔 struggling, 2=😕 low, 3=😐 okay, 4=🙂 good, 5=😊 great |
| energy | int | 1-5 |
| note | text | Optional, short |
| created_at | datetime | |

### ScheduleBlock

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| date | date | Which day |
| start_time | time | Block start |
| end_time | time | Block end |
| title | string | Task name |
| goal_id | int | FK to Goal (nullable) |
| habit_id | int | FK to Habit (nullable) |
| direction_id | int | FK to Direction (for bubble color). Nullable — blocks without direction (e.g., "Lunch") get no bubble, just open space |
| block_type | enum | goal / habit / custom |
| status | enum | planned / done / skipped |
| generated_by | enum | gucci / user |

**Constraint**: at most one of `goal_id` / `habit_id` should be non-null. `block_type=custom` means neither is set (e.g., breaks, personal time — these are NOT rendered as bubbles on the Day canvas, preserving free-time feel).

### ChatMessage

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| role | enum | user / gucci |
| content | text | Message text |
| context_type | enum | general / goal |
| goal_id | int | FK to Goal (nullable, for goal-specific chats) |
| created_at | datetime | |

### ShadowInsight

| Field | Type | Description |
|---|---|---|
| id | int | Primary key |
| insight_type | string | e.g., "energy_pattern", "avoidance", "mood_trigger" |
| content | text | What Gucci learned |
| confidence | float | 0-1, how sure |
| used | bool | Whether Gucci has acted on it |
| created_at | datetime | |

---

## 5. Pages & UI

### Global Design Language

- **Corners**: 16-24px radius everywhere — soft, bubble-like
- **Shadows**: subtle, warm (light theme: soft drop shadow; dark theme: soft glow)
- **Typography**: rounded font (Nunito or Quicksand), friendly weight
- **Opacity**: bubble fills at 20% goal color, borders at 60%
- **Animations**: gentle, no fast movements — ease-in-out, 300-400ms
- **Spacing**: generous whitespace — content breathes
- **Everything floats**: cards, bubbles, buttons — nothing feels anchored to a grid

### Themes

**Light theme**:
- Background: `#FFF8F0` (warm cream)
- Cards: `#FFFFFF` with warm shadow
- Text: `#3D3440` (dark plum)
- Time hints: `#3D3440` at 20% opacity
- Greenhouse garden: sunny, warm light through glass

**Dark theme**:
- Background: `#1A1520` (deep plum)
- Cards: `#252030` with soft glow
- Text: `#E8DFE5` (warm off-white)
- Time hints: `#E8DFE5` at 20% opacity
- Greenhouse garden: moonlit, soft blue-white light, fireflies

### Navigation — Bottom Bar

4 pill-shaped tabs:
```
╭──────╮ ╭──────╮ ╭──────╮ ╭──────╮
│  🐱  │ │  🎯  │ │  📅  │ │  👤  │
│Gucci │ │Goals │ │ Day  │ │  Me  │
╰──────╯ ╰──────╯ ╰──────╯ ╰──────╯
```
- Active tab: filled with accent color, gentle scale-up
- Inactive: outline only
- Gucci tab is default on app open

---

### Page 1: Gucci (Home)

**Background**: Japanese zen greenhouse — minimalist, precise, warm. Bamboo, moss, carefully placed stones, glass walls with soft filtered light. Feng shui inspired layout. Style: looks like you're inside a greenhouse.

**Gucci**: centered, always full-form (not growing). Rabbit-cat spirit hybrid with subtle aura glow. Expressions change: happy, cozy, sleepy, concerned.

**Behavior on open**: Gucci speaks first immediately. Greeting is context-aware:
- Morning: "Good morning! How did you sleep?"
- Afternoon: "Hey, how's the day going?"
- After good day: "Yesterday was great, you did 4 out of 5!"
- After inactivity: "I missed you. Everything okay?"

**Elements**:
- Gucci (tappable — animation + encouraging line)
- Mood bubbles (3-5 emoji options, optional tap)
- Today's habits as small checkmark bubbles
- Chat input always visible at bottom
- Gucci's AI greeting bubble (speaks first)

**First-time onboarding**: No forms, no wizard. Gucci starts a conversation:
1. "Hey! I'm Gucci, your spirit guide. What's on your mind lately?"
2. Through natural dialogue, Gucci learns: goals, current habits, schedule, energy patterns
3. Gucci uses psychology to extract info — never feels like a questionnaire
4. After conversation, Gucci silently creates: directions, goals, habits, initial schedule

---

### Page 2: Goals

**Two modes** (toggle button):

**Mode 1: By Direction** (default)
- Sections grouped by direction (Career, Health, Mind, Life)
- Each goal is a rounded card with:
  - Icon + title
  - Progress bar (soft, rounded)
  - Next step preview
  - Tap → opens sub-agent chat for that specific goal

**Mode 2: Daily Board**
- All today's goal steps on one flat list
- Each item is a bubble colored by direction
- Tap → sub-agent chat
- Checkmark to complete

**Sub-agent chat (per goal)**:
- Opens full-screen chat view
- Header shows goal name + direction color
- Gucci talks specifically about THIS goal
- Can: break into steps, give advice, help think through blockers, suggest resources
- "Done" button available in chat to mark step complete
- Chat history preserved per goal — context carries across days

**Agent architecture**: All sub-agents are Gucci with different system prompts. User sees the same companion, but the AI context is focused on the specific goal domain.

---

### Page 3: Day (Flowing Time Canvas)

**Background**: continuous vertical gradient representing time of day
- Morning zone: warm amber/peach tint
- Midday: bright/light
- Evening: cool lavender/indigo
- Busy zones (where bubbles are): slightly darker/more tinted
- Free zones: lighter, more contrasting — spacious feeling

**Time markers**: tiny numbers at left edge, very low opacity. They guide without demanding attention. Present only at hour boundaries.

**Task bubbles**:
- Oval/pill shape, colored by direction (20% fill, 60% border)
- Height proportional to task duration (20min = small, 2h = tall)
- Float in the gradient at their time position
- Text truncates with `...` if too long

**Tap bubble → popup**:
- Expands from the bubble position
- Same rounded bubble aesthetic
- Shows: full task name, description, linked goal, duration
- Two buttons: 💬 (chat with Gucci about it) and ✓ (mark done)

**Free time**: no bubbles, just calm open gradient. The visual weight of your day is immediately felt — heavy day = many bubbles, light day = lots of open space.

**Navigation**: swipe left/right for previous/next day.

**Schedule generation**:
- First time: Gucci builds through onboarding conversation
- Daily: Gucci proposes tomorrow's schedule each evening
- Based on: active goals, pending steps, habit schedule, user's energy patterns, recent mood
- User can: accept, edit, or ask Gucci to rebuild
- "Plan tomorrow" button available

---

### Page 4: Me

**Clean minimal background** (no garden).

**Content**:
- Weekly mood heatmap (colored dots for each day)
- Habit completion rate (simple fraction, not percentage)
- Current streak (gentle, no punishment for breaking)
- Garden stage indicator + Gucci's current aura color
- Mood trend arrow (improving / stable / declining)

**Settings section**:
- Language toggle: RU / EN
- Theme toggle: Light / Dark
- Notification preferences
- API key input (Claude)
- Wake time (for schedule generation)

---

## 6. AI Coach — Gucci's Brain

### System Prompt (Core)

Gucci's personality:
- Warm, friendly, slightly mystical — like a wise cat who happens to talk
- Uses gentle psychology — never confrontational
- Bilingual (RU/EN) — matches user's language preference
- Doesn't lecture — asks questions that lead to self-discovery
- Celebrates small wins genuinely
- When user is struggling: validates feelings first, then gently suggests one tiny action

### Shadow Analysis

**Mechanism**: Rule-based heuristics, NOT AI calls. Runs locally after each habit log and daily at midnight. No API cost.

**How it works**:
1. After each habit log: update running stats (completion rates per habit, per weekday, per time-of-day)
2. Daily midnight job: analyze last 7-14 days of data, generate/update insights
3. Confidence score: based on sample size (3 data points = 0.3, 7 = 0.6, 14+ = 0.9)

**Insight types and their rules**:
- **energy_pattern**: Track `logged_at` times on HabitLog — if 70%+ of completions happen before noon → "morning person" insight. Confidence = completions / 14
- **avoidance_pattern**: If a goal has 0 step completions in 7+ days while other goals are active → "avoiding {goal}" insight. Confidence = days_avoided / 14
- **mood_activity_correlation**: Compare average mood on days habit X was done vs not done. If delta > 0.5 → "{habit} improves mood" insight. Confidence = min(sample_days / 14, 1.0)
- **schedule_adherence**: Compare planned schedule blocks to actual habit logs. If <50% match → "schedule doesn't match reality" insight
- **streak_pattern**: Track consecutive completion days per habit

Gucci uses insights naturally in conversation — never says "my analysis shows...", instead: "I noticed you usually feel better on days you work out in the morning. Want to try that tomorrow?"

### Context Building for API Calls

Each Haiku API call includes:
```
System prompt (Gucci personality + rules)
+ User profile (name, goals summary, current habits)
+ Recent mood entries (last 7 days)
+ Recent habit completion (last 7 days)
+ Active shadow insights (confidence > 0.6)
+ Last 10 chat messages (for continuity)
+ [For goal chats: goal details, steps, goal chat history]
```

Estimated tokens per call: ~800 input, ~200 output = ~$0.005 per interaction (Sonnet pricing: $3/$15 per M tokens).

### Notification Intelligence

- **Deadline-based**: if a goal step has a deadline, remind 1 day before and morning-of
- **Pattern-based**: if user usually works out at 7am but hasn't logged by 8am, gentle nudge
- **Plan-based**: if tomorrow has a generated schedule, evening reminder to review it
- **Anti-annoyance rule**: max 3 notifications per day, never back-to-back, never after 22:00

---

## 7. Onboarding Flow

No forms. No tutorials. Just Gucci.

1. App opens → greenhouse with Gucci
2. Gucci: "Hey! I'm Gucci, your spirit companion. What's your name?"
3. Natural conversation flows:
   - What are you working towards?
   - What does a typical day look like?
   - What habits have you been wanting to build?
   - What's been hardest about staying consistent?
4. **Entity extraction**: After sufficient conversation (3+ user messages), Gucci calls `POST /api/onboarding/extract` which:
   - Sends the full conversation to Sonnet with a structured-output system prompt
   - System prompt instructs Haiku to return JSON: `{directions: [], goals: [], habits: [], schedule_hints: {}}`
   - Flask validates the JSON and creates entities in the database
   - If extraction seems incomplete, Gucci asks one more natural question to fill gaps
5. Gucci: "I put together a plan based on what you told me. Want to check it out?"
6. User sees a **review card** showing extracted: directions, goals, habits, suggested wake time
7. User can: confirm all, edit individual items, or ask Gucci to adjust
8. On confirm → `onboarded` setting set to true, initial schedule generated
9. Done. App is personalized.

**If extraction fails** (API error, invalid JSON): Gucci says "I'm having trouble organizing my thoughts. Mind telling me one more time — what's the most important thing you want to work on?" and retries.

---

## 8. Garden — Japanese Zen Greenhouse

### Style
- **Feng shui** inspired placement — nothing random
- **Japanese accuracy** — minimalist, precise, intentional
- **Greenhouse** feel — glass walls, filtered natural light, contained warmth
- Indoor garden with outdoor beauty

### Elements by Stage

| Stage | XP | Elements |
|---|---|---|
| 0 | 0 | Bare earth floor, empty glass walls, morning light |
| 1 | 50 | Moss patches appear |
| 2 | 150 | Small zen stones placed carefully |
| 3 | 300 | Bamboo sprout in corner |
| 4 | 500 | Zen stone arrangement (karesansui) |
| 5 | 800 | Ferns and small plants |
| 6 | 1200 | Bonsai tree on wooden stand |
| 7 | 1800 | Small water feature (tsukubai) |
| 8 | 2500 | Flowering plants (orchids, wisteria) |
| 9 | 3500 | Full greenhouse — hanging plants, warm glow, fireflies at night |

### Theme Variations
- **Light theme**: sunny, warm golden light through glass, green vibrant
- **Dark theme**: moonlit, cool blue-white light, fireflies, gentle shadows

### Garden never dies
- Inactive user: garden pauses at current stage
- No wilting, no dying plants
- When user returns, Gucci says "the garden's been waiting for you" — not guilt, just warmth

---

## 9. PWA Configuration

### Manifest
- Name: MishaGo
- Short name: MishaGo
- Theme color: `#FFF8F0` (light) / `#1A1520` (dark)
- Background color: matches theme
- Display: standalone (no browser bar)
- Orientation: portrait
- Icons: Gucci silhouette at various sizes

### Service Worker
- Cache-first for static assets (Gucci animations, garden SVGs)
- Network-first for API calls
- Offline: show cached Gucci page with "I'm waiting for connection" message
- Background sync for habit logs made offline

### Install Prompt
- After 3rd visit, suggest "Add to Home Screen"
- Gucci says: "Want me closer? You can add me to your home screen!"

---

## 10. Non-Functional Requirements

- **Performance**: First contentful paint < 2s, API responses < 500ms (excluding AI)
- **AI response**: streaming, first token < 1s
- **Offline**: basic habit logging works offline, syncs when online
- **Storage**: SQLite file < 50MB for years of data
- **Cost**: ~$1.50/month for AI at 10 interactions/day (Claude Sonnet 4.6)
- **Security**: API key stored locally, never sent to any server except Anthropic
- **Privacy**: all data stays on device / local server. No cloud sync. No analytics.
- **Concurrency**: SQLite in WAL mode for safe concurrent reads during background sync.
- **AI assets**: Gucci Lottie animations and garden SVGs to be created as part of implementation (placeholder static images for MVP).

---

## 11. Error Handling

| Scenario | Behavior |
|---|---|
| Claude API down / timeout | Gucci says "I'm a bit sleepy right now... try again in a moment?" + retry button |
| Invalid API key | Settings page highlights API key field with "This key doesn't seem to work" |
| No goals yet (Goals page) | Show Gucci illustration + "Let's set your first goal! Tap to chat with me" |
| No schedule yet (Day page) | Show empty gradient + floating "Ask Gucci to plan your day" button |
| Schedule generation fails | Gucci: "Couldn't plan tomorrow — want to try again or build it yourself?" |
| Offline | Habit logs queued locally, chat shows "I need internet to think" |
| Onboarding extraction fails | Gucci asks a simpler follow-up question, retries extraction |

---

## 12. Out of Scope (v1)

- Social features (friends, sharing)
- Multiple users
- Cloud sync / backup (manual SQLite export is fine)
- Audio recording tasks
- Calendar integration (Google Calendar, etc.)
- Desktop-specific layout (mobile-first only)
- App store distribution (PWA only)
