# MishaGo — Project Report

**Date**: 2026-03-15
**Repository**: https://github.com/madaramvk/MishaGo
**Location**: `D:\Pet-projects\MishaGo\`

---

## Summary

MishaGo is a personal wellness PWA organizer with an AI spirit companion named **Gucci** (rabbit-cat hybrid). Built in a single session from brainstorm to working app.

### Stats
- **45 commits**, clean git history
- **47 source files** (1,595 lines Python + 3,572 lines React/CSS)
- **32 backend tests**, all passing
- **~$1.50/month** AI cost (Claude Sonnet 4.6)

---

## Architecture

| Layer | Technology |
|---|---|
| Backend | Flask (Python 3.14) — REST API + SSE streaming |
| Frontend | React 18 (Vite) — PWA |
| Database | SQLite (WAL mode) |
| AI | Claude Sonnet 4.6 (chat, schedule gen, onboarding extraction) |
| Design | CSS art (Gucci character), glassmorphism, nature gradients |

### Data Model (11 tables)
Setting, Pet, Direction, Goal, GoalStep, Habit, HabitLog, MoodEntry, ScheduleBlock, ChatMessage, ShadowInsight

### API Endpoints (21)
- Settings: GET/PUT
- Pet: GET, GET /mind
- Habits: GET/POST/PUT, POST /log, GET /log/:date
- Goals: GET/POST/PUT, GET/POST/PUT steps
- Directions: GET/POST
- Mood: GET/POST
- Schedule: GET/POST/PUT, POST /generate
- Chat: GET /history, GET /stream, GET /goal/:id/stream
- Onboarding: POST /extract

---

## Features Implemented

### Core
1. **Gucci AI Companion** — chat via SSE streaming, context-aware responses
2. **Onboarding** — natural conversation (3-4 exchanges) → auto-creates goals, habits, settings
3. **Goal Management** — expandable cards with step checklists, tap to check off, progress auto-calculates
4. **Habit Tracking** — daily checkmarks on Gucci page, XP rewards, floating "+XP" animation
5. **Mood Logging** — 5-emoji picker, weekly heatmap on Me page

### AI Features
6. **Goal Sub-Agent Chat** — tap any goal → focused conversation with Gucci about that specific goal
7. **Schedule Generation** — AI creates daily plan based on goals, habits, energy patterns
8. **Smart Replan** — 4 intensity modes: Gucci auto-decides, Light, Balanced, Intense
9. **Shadow Analyzer** — rule-based pattern detection (energy, avoidance, mood correlation, streaks, schedule adherence)
10. **Behavioral Insights** — shadow insights feed into AI context for smarter responses

### Design
11. **Gucci Character** — full CSS art: ears, eyes (blinking), whiskers, body, arms (waving), feet, tail (wagging), mood expressions
12. **Zen Greenhouse Garden** — 10 evolution stages (0-9), progressively richer visual layers
13. **Day Canvas** — 4-row timeline (Morning/Day/Evening/Night) with nature backgrounds (sunrise, clouds, sunset, stars+moon)
14. **Glassmorphism** — frosted glass chat bubbles, input bar, nav bar
15. **Dark/Light Theme** — full theme system with CSS variables
16. **Typography** — Cormorant Garamond (display) + DM Sans (body)

### Infrastructure
17. **PWA** — manifest, service worker, installable on Android
18. **Error Boundary** — catches React crashes, shows friendly message
19. **Gucci's Mind** — debug panel showing AI's internal state (profile, goals, habits, insights, mood reasoning)
20. **Bilingual** — RU/EN support for all AI interactions

---

## Pages

| Page | Features |
|---|---|
| **Gucci Home** | Garden background, animated Gucci, chat, mood picker, habit chips |
| **Goals** | Direction groups + daily board toggle, expandable step checklists |
| **Day** | Nature timeline (4 rows), task bubbles, popup details, replan with modes |
| **Me** | Mood heatmap, XP/garden stats, Gucci's Mind, settings |

---

## Manual Test Checklist

### Setup
- [ ] Start backend: `cd "D:\Pet-projects\MishaGo" && python -m backend.app`
- [ ] Start frontend: `cd "D:\Pet-projects\MishaGo\frontend" && npm run dev`
- [ ] Open `http://localhost:5173` in browser

### Onboarding (first time)
- [ ] Fresh DB → Gucci greets and asks questions
- [ ] Answer 3-4 questions about name, goals, habits, wake time
- [ ] Gucci summarizes and says "I'll set things up"
- [ ] Goals tab shows created goals
- [ ] Gucci Home shows habit chips
- [ ] Me → Gucci's Mind shows profile with name, onboarded=true

### Gucci Chat
- [ ] Type message → Gucci responds via streaming (text appears word by word)
- [ ] Chat history preserved across page navigations
- [ ] Different greeting for morning/afternoon/evening
- [ ] No auto-greeting if already chatted today
- [ ] Switch language in Settings → Gucci responds in that language

### Goals
- [ ] Goals grouped by direction (Career, Health, Mind, Life)
- [ ] Toggle "All" mode → shows only goals with pending steps
- [ ] Tap goal → expands step checklist
- [ ] Tap step → toggles done/undone (circle ○ ↔ checkmark ✓)
- [ ] Progress bar updates after checking step
- [ ] "Discuss with Gucci" button → opens goal-specific chat
- [ ] Goal chat stays focused on that goal, doesn't ask about mood/hobbies

### Habits
- [ ] Habit chips on Gucci Home page
- [ ] Tap chip → marks done (accent color)
- [ ] "+XP" float animation appears
- [ ] Tap again → unmarks
- [ ] Only today's habits shown (weekday filter works)

### Day Canvas
- [ ] 4 rows: Morning, Day, Evening, Night with nature backgrounds
- [ ] Stars twinkling on Night row, moon glowing
- [ ] Clouds drifting on Day row
- [ ] "Ask Gucci to plan this day" button when empty
- [ ] Tap → schedule generates (bubbles appear)
- [ ] Tap bubble → popup with title, time, Done/Close buttons
- [ ] Goal-linked bubbles have "Discuss" button in popup
- [ ] 🔄 floating button → opens mode selector
- [ ] "Let Gucci decide" auto-picks intensity from mood/habit data
- [ ] Light/Balanced/Intense generate different schedules
- [ ] ◀ ▶ arrows navigate between days

### Mood
- [ ] Tap mood emoji on Gucci Home → logs mood
- [ ] Me page shows weekly mood heatmap (7 dots)
- [ ] Mood trend average shown

### Me Page
- [ ] Stats: mood avg, garden stage, XP
- [ ] Gucci's Mind → tap to expand → shows profile, goals, habits, insights, mood reasoning
- [ ] Theme toggle: Dark ↔ Light
- [ ] Language toggle: RU ↔ EN
- [ ] Wake time input works
- [ ] API key save works

### Shadow Analyzer
- [ ] Complete habits for several days → shadow insights appear in Gucci's Mind
- [ ] Insights include: energy patterns, avoidance, mood-activity correlation
- [ ] Gucci uses insights naturally in conversation ("I noticed you feel better when...")

### PWA
- [ ] Chrome shows "Install" prompt after 3+ visits
- [ ] App works in standalone mode (no browser bar)

### Error Handling
- [ ] Remove API key → chat shows "sleepy" error message
- [ ] Invalid API key → Settings shows error
- [ ] Blank page on crash → ErrorBoundary shows "Gucci is confused" + refresh button

---

## Known Limitations (v1)
- No push notifications (needs HTTPS/service worker push)
- No cloud sync (SQLite local only)
- Gucci art is CSS — custom illustration would look better
- No delete goal/habit from UI (only via DB)
- Schedule doesn't link habit_id/goal_id perfectly (fuzzy name matching)
- Single user only
- Desktop layout not optimized (mobile-first 430px max)

---

## Next Steps (if continuing)
1. Custom Gucci illustration (AI-generated or commissioned)
2. Push notifications for deadlines and schedule reminders
3. Delete/edit goals and habits from UI
4. Cloud backup (export/import JSON)
5. Gucci voice (TTS for responses)
6. Weekly review — Gucci summarizes your week
7. Deploy to free hosting (Railway/Render backend + Vercel frontend)
