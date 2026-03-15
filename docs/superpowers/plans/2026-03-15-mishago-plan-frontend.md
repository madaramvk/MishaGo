# MishaGo Frontend Implementation Plan (Chunks 3-4)

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the React PWA frontend — 4 pages (Gucci Home, Goals, Day Canvas, Me), themes, PWA setup.

**Architecture:** React 18 (Vite), React Router, CSS modules with CSS variables for theming, SSE via EventSource API.

**Spec:** `docs/superpowers/specs/2026-03-15-mishago-design.md`
**Backend plan:** `docs/superpowers/plans/2026-03-15-mishago-plan.md`

---

## Chunk 3: React Setup + Theme + Navigation + Core Components

### Task 13: Vite + React Project Setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/api.js`

- [ ] **Step 1: Initialize React project with Vite**

```bash
cd "D:\Pet-projects\MishaGo"
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install react-router-dom
```

- [ ] **Step 2: Create `frontend/src/api.js`** — centralized API client

```javascript
const API_BASE = "http://localhost:5000/api";

export async function fetchJSON(path, options = {}) {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  return resp.json();
}

export function streamSSE(path, onChunk, onDone, onError) {
  const source = new EventSource(`${API_BASE}${path}`);
  source.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.done) {
      source.close();
      onDone?.();
    } else if (data.error) {
      source.close();
      onError?.(data.error);
    } else {
      onChunk(data.text);
    }
  };
  source.onerror = () => {
    source.close();
    onError?.("Connection lost");
  };
  return source;
}
```

- [ ] **Step 3: Create `frontend/src/App.jsx`** — router + theme provider

```jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";
import NavBar from "./components/NavBar";
import GucciHome from "./pages/GucciHome";
import Goals from "./pages/Goals";
import DayCanvas from "./pages/DayCanvas";
import Me from "./pages/Me";
import GoalChat from "./components/GoalChat";
import "./themes/variables.css";
import "./App.css";

export default function App() {
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <div className="app">
        <div className="page-content">
          <Routes>
            <Route path="/" element={<GucciHome />} />
            <Route path="/goals" element={<Goals />} />
            <Route path="/goals/:goalId/chat" element={<GoalChat />} />
            <Route path="/day" element={<DayCanvas />} />
            <Route path="/me" element={<Me setTheme={setTheme} theme={theme} />} />
          </Routes>
        </div>
        <NavBar />
      </div>
    </BrowserRouter>
  );
}
```

- [ ] **Step 4: Create `frontend/src/App.css`**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Nunito", "Quicksand", sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  max-width: 430px;
  margin: 0 auto;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 72px; /* space for navbar */
}
```

- [ ] **Step 5: Verify it runs**

```bash
cd "D:\Pet-projects\MishaGo\frontend"
npm run dev
```

Open http://localhost:5173 — should show blank page with no errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: React + Vite project setup with router and API client"
```

---

### Task 14: Theme System (CSS Variables)

**Files:**
- Create: `frontend/src/themes/variables.css`

- [ ] **Step 1: Create `frontend/src/themes/variables.css`**

```css
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

:root,
[data-theme="light"] {
  --bg: #FFF8F0;
  --bg-card: #FFFFFF;
  --text: #3D3440;
  --text-muted: rgba(61, 52, 64, 0.5);
  --text-hint: rgba(61, 52, 64, 0.2);
  --shadow: 0 2px 12px rgba(61, 52, 64, 0.08);
  --glow: none;
  --nav-bg: rgba(255, 248, 240, 0.9);

  /* Direction colors */
  --color-career: #7EB8DA;
  --color-health: #9DD6A3;
  --color-mind: #C4A8E0;
  --color-life: #F0C987;

  /* Bubble opacity */
  --bubble-fill: 0.2;
  --bubble-border: 0.6;

  /* Accent */
  --accent: #C4A8E0;
  --accent-soft: rgba(196, 168, 224, 0.2);

  /* Garden */
  --garden-light: rgba(255, 248, 240, 0.3);

  /* Day gradient */
  --day-morning: #FFF0E0;
  --day-midday: #FFFDF8;
  --day-evening: #F0E8F8;
  --day-busy: rgba(61, 52, 64, 0.04);
}

[data-theme="dark"] {
  --bg: #1A1520;
  --bg-card: #252030;
  --text: #E8DFE5;
  --text-muted: rgba(232, 223, 229, 0.5);
  --text-hint: rgba(232, 223, 229, 0.2);
  --shadow: none;
  --glow: 0 0 20px rgba(196, 168, 224, 0.1);
  --nav-bg: rgba(26, 21, 32, 0.9);

  --color-career: #7EB8DA;
  --color-health: #9DD6A3;
  --color-mind: #C4A8E0;
  --color-life: #F0C987;

  --bubble-fill: 0.15;
  --bubble-border: 0.4;

  --accent: #C4A8E0;
  --accent-soft: rgba(196, 168, 224, 0.15);

  --garden-light: rgba(196, 168, 224, 0.05);

  --day-morning: #251D1A;
  --day-midday: #1A1520;
  --day-evening: #1A1530;
  --day-busy: rgba(232, 223, 229, 0.03);
}
```

- [ ] **Step 2: Verify both themes render correctly**

Toggle `data-theme` in browser DevTools between "light" and "dark".

- [ ] **Step 3: Commit**

```bash
git add frontend/src/themes/
git commit -m "feat: light and dark theme CSS variables"
```

---

### Task 15: NavBar Component

**Files:**
- Create: `frontend/src/components/NavBar.jsx`
- Create: `frontend/src/components/NavBar.css`

- [ ] **Step 1: Create `frontend/src/components/NavBar.jsx`**

```jsx
import { NavLink } from "react-router-dom";
import "./NavBar.css";

const tabs = [
  { path: "/", icon: "🐱", label: "Gucci" },
  { path: "/goals", icon: "🎯", label: "Goals" },
  { path: "/day", icon: "📅", label: "Day" },
  { path: "/me", icon: "👤", label: "Me" },
];

export default function NavBar() {
  return (
    <nav className="navbar">
      {tabs.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          className={({ isActive }) => `nav-tab ${isActive ? "active" : ""}`}
          end={tab.path === "/"}
        >
          <span className="nav-icon">{tab.icon}</span>
          <span className="nav-label">{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
```

- [ ] **Step 2: Create `frontend/src/components/NavBar.css`**

```css
.navbar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 430px;
  display: flex;
  justify-content: space-around;
  padding: 8px 16px 12px;
  background: var(--nav-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  z-index: 100;
}

.nav-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 16px;
  border-radius: 20px;
  text-decoration: none;
  color: var(--text-muted);
  transition: all 0.3s ease;
  border: 1.5px solid transparent;
}

.nav-tab.active {
  background: var(--accent-soft);
  color: var(--text);
  border-color: var(--accent);
  transform: scale(1.05);
}

.nav-icon {
  font-size: 20px;
}

.nav-label {
  font-size: 11px;
  font-weight: 600;
}
```

- [ ] **Step 3: Verify navigation works**

Click all 4 tabs — each should highlight with accent color and show correct page.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/NavBar.*
git commit -m "feat: pill-shaped bottom NavBar with 4 tabs"
```

---

### Task 16: Chat Components (Shared)

**Files:**
- Create: `frontend/src/components/ChatBubble.jsx`
- Create: `frontend/src/components/ChatBubble.css`
- Create: `frontend/src/hooks/useChat.js`

- [ ] **Step 1: Create `frontend/src/hooks/useChat.js`**

```javascript
import { useState, useCallback, useRef } from "react";
import { fetchJSON, streamSSE } from "../api";

export default function useChat(contextType = "general", goalId = null) {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const sourceRef = useRef(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      let path = `/chat/history?context_type=${contextType}&limit=20`;
      if (goalId) path += `&goal_id=${goalId}`;
      const data = await fetchJSON(path);
      setMessages(data);
    } catch (e) {
      console.error("Failed to load chat history:", e);
    }
    setLoading(false);
  }, [contextType, goalId]);

  const send = useCallback((text) => {
    if (!text.trim() || streaming) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setStreaming(true);

    let accumulated = "";
    const path = goalId
      ? `/chat/goal/${goalId}/stream?message=${encodeURIComponent(text)}`
      : `/chat/stream?message=${encodeURIComponent(text)}`;

    setMessages((prev) => [...prev, { role: "gucci", content: "" }]);

    sourceRef.current = streamSSE(
      path,
      (chunk) => {
        accumulated += chunk;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "gucci", content: accumulated };
          return updated;
        });
      },
      () => setStreaming(false),
      (error) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "gucci",
            content: "I'm a bit sleepy right now... try again in a moment? 😴",
          };
          return updated;
        });
        setStreaming(false);
      }
    );
  }, [streaming, goalId]);

  const stop = useCallback(() => {
    sourceRef.current?.close();
    setStreaming(false);
  }, []);

  return { messages, streaming, loading, loadHistory, send, stop };
}
```

- [ ] **Step 2: Create `frontend/src/components/ChatBubble.jsx`**

```jsx
import "./ChatBubble.css";

export default function ChatBubble({ role, content, streaming }) {
  return (
    <div className={`chat-bubble ${role}`}>
      <div className={`bubble-content ${streaming ? "streaming" : ""}`}>
        {content}
        {streaming && <span className="cursor">▍</span>}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `frontend/src/components/ChatBubble.css`**

```css
.chat-bubble {
  display: flex;
  margin: 8px 16px;
  animation: fadeUp 0.3s ease;
}

.chat-bubble.gucci {
  justify-content: flex-start;
}

.chat-bubble.user {
  justify-content: flex-end;
}

.bubble-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 20px;
  font-size: 15px;
  line-height: 1.5;
  box-shadow: var(--shadow);
}

.chat-bubble.gucci .bubble-content {
  background: var(--bg-card);
  color: var(--text);
  border-bottom-left-radius: 6px;
}

.chat-bubble.user .bubble-content {
  background: var(--accent-soft);
  color: var(--text);
  border-bottom-right-radius: 6px;
}

.cursor {
  animation: blink 1s infinite;
  color: var(--accent);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ChatBubble.* frontend/src/hooks/useChat.js
git commit -m "feat: chat bubble component + useChat hook with SSE streaming"
```

---

### Task 17: MoodPicker Component

**Files:**
- Create: `frontend/src/components/MoodPicker.jsx`
- Create: `frontend/src/components/MoodPicker.css`

- [ ] **Step 1: Create `frontend/src/components/MoodPicker.jsx`**

```jsx
import { useState } from "react";
import { fetchJSON } from "../api";
import "./MoodPicker.css";

const moods = [
  { value: 1, emoji: "😔", label: "struggling" },
  { value: 2, emoji: "😕", label: "low" },
  { value: 3, emoji: "😐", label: "okay" },
  { value: 4, emoji: "🙂", label: "good" },
  { value: 5, emoji: "😊", label: "great" },
];

export default function MoodPicker({ onMoodSelected }) {
  const [selected, setSelected] = useState(null);

  const handleTap = async (mood) => {
    setSelected(mood.value);
    try {
      await fetchJSON("/mood", {
        method: "POST",
        body: JSON.stringify({ mood: mood.value, energy: mood.value }),
      });
      onMoodSelected?.(mood);
    } catch (e) {
      console.error("Failed to log mood:", e);
    }
  };

  return (
    <div className="mood-picker">
      {moods.map((m) => (
        <button
          key={m.value}
          className={`mood-bubble ${selected === m.value ? "selected" : ""}`}
          onClick={() => handleTap(m)}
        >
          <span className="mood-emoji">{m.emoji}</span>
          <span className="mood-label">{m.label}</span>
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create `frontend/src/components/MoodPicker.css`**

```css
.mood-picker {
  display: flex;
  gap: 8px;
  justify-content: center;
  padding: 12px 16px;
}

.mood-bubble {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 20px;
  border: 1.5px solid var(--text-hint);
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text);
}

.mood-bubble:hover,
.mood-bubble.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
  transform: scale(1.1);
}

.mood-emoji {
  font-size: 24px;
}

.mood-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/MoodPicker.*
git commit -m "feat: MoodPicker component with 5 emoji bubbles"
```

---

### Task 18: Gucci Home Page

**Files:**
- Create: `frontend/src/pages/GucciHome.jsx`
- Create: `frontend/src/pages/GucciHome.css`
- Create: `frontend/src/components/Gucci.jsx`
- Create: `frontend/src/components/Gucci.css`

- [ ] **Step 1: Create Gucci placeholder component**

```jsx
// frontend/src/components/Gucci.jsx
import "./Gucci.css";

const expressions = {
  happy: "😸",
  content: "😺",
  cozy: "😻",
  sleepy: "😴",
  concerned: "🥺",
};

export default function Gucci({ mood = "content", onClick }) {
  return (
    <div className="gucci-container" onClick={onClick}>
      <div className="gucci-aura" />
      <div className="gucci-body">
        <span className="gucci-face">{expressions[mood] || "😺"}</span>
      </div>
      <div className="gucci-name">Gucci</div>
    </div>
  );
}
```

```css
/* frontend/src/components/Gucci.css */
.gucci-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  position: relative;
}

.gucci-aura {
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--accent-soft) 0%, transparent 70%);
  animation: pulse 3s ease-in-out infinite;
}

.gucci-body {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow);
  position: relative;
  z-index: 1;
  transition: transform 0.3s ease;
}

.gucci-body:active {
  transform: scale(0.95);
}

.gucci-face {
  font-size: 48px;
}

.gucci-name {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 1px;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.15); opacity: 0.3; }
}
```

- [ ] **Step 2: Create `frontend/src/pages/GucciHome.jsx`**

```jsx
import { useEffect, useState, useRef } from "react";
import { fetchJSON } from "../api";
import useChat from "../hooks/useChat";
import Gucci from "../components/Gucci";
import MoodPicker from "../components/MoodPicker";
import ChatBubble from "../components/ChatBubble";
import "./GucciHome.css";

export default function GucciHome() {
  const [pet, setPet] = useState({ mood: "content", garden_stage: 0, xp: 0 });
  const [habits, setHabits] = useState([]);
  const [habitLogs, setHabitLogs] = useState({});
  const { messages, streaming, loadHistory, send } = useChat("general");
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchJSON("/pet").then(setPet).catch(console.error);
    fetchJSON("/habits?today=true").then(setHabits).catch(console.error);
    const today = new Date().toISOString().split("T")[0];
    fetchJSON(`/habits/log/${today}`).then((logs) => {
      const map = {};
      logs.forEach((l) => (map[l.habit_id] = l.completed));
      setHabitLogs(map);
    }).catch(console.error);
    loadHistory();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Gucci speaks first if no messages
  useEffect(() => {
    if (messages.length === 0 && !streaming) {
      const hour = new Date().getHours();
      let greeting;
      if (hour < 12) greeting = "Good morning! How are you feeling today? ☀️";
      else if (hour < 18) greeting = "Hey! How's the day going? 🌤";
      else greeting = "Good evening! How was your day? 🌙";

      // Only send auto-greeting if we have an API key set up
      fetchJSON("/settings").then((settings) => {
        if (settings.api_key && settings.onboarded === "true") {
          send(greeting.replace(/[☀️🌤🌙]/g, "").trim());
        }
      }).catch(() => {});
    }
  }, [messages.length]);

  const toggleHabit = async (habitId, xpReward) => {
    const today = new Date().toISOString().split("T")[0];
    const newState = !habitLogs[habitId];
    setHabitLogs((prev) => ({ ...prev, [habitId]: newState }));
    try {
      await fetchJSON("/habits/log", {
        method: "POST",
        body: JSON.stringify({ habit_id: habitId, date: today, completed: newState }),
      });
      if (newState) setPet((p) => ({ ...p, xp: p.xp + xpReward }));
    } catch (e) {
      setHabitLogs((prev) => ({ ...prev, [habitId]: !newState }));
    }
  };

  const handleSend = () => {
    if (!input.trim()) return;
    send(input);
    setInput("");
  };

  return (
    <div className="gucci-home">
      {/* Garden background */}
      <div className={`garden garden-stage-${pet.garden_stage}`} />

      {/* Gucci */}
      <Gucci mood={pet.mood} />

      {/* Chat messages */}
      <div className="chat-area">
        {messages.map((m, i) => (
          <ChatBubble
            key={i}
            role={m.role}
            content={m.content}
            streaming={streaming && i === messages.length - 1 && m.role === "gucci"}
          />
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Mood picker */}
      <MoodPicker onMoodSelected={(m) => setPet((p) => ({ ...p, mood: "happy" }))} />

      {/* Today's habits */}
      <div className="habit-row">
        {habits.map((h) => (
          <button
            key={h.id}
            className={`habit-chip ${habitLogs[h.id] ? "done" : ""}`}
            onClick={() => toggleHabit(h.id, h.xp_reward)}
          >
            {h.icon} {habitLogs[h.id] ? "✓" : ""}
          </button>
        ))}
      </div>

      {/* Chat input */}
      <div className="chat-input-bar">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Talk to Gucci..."
        />
        <button className="send-btn" onClick={handleSend} disabled={streaming}>
          ↑
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create `frontend/src/pages/GucciHome.css`**

```css
.gucci-home {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
}

.garden {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  background: var(--bg);
  /* Garden stages add layers via additional CSS classes */
}

.garden-stage-0 { /* bare earth — just bg color */ }
.garden-stage-1 { background-image: radial-gradient(ellipse at 30% 80%, rgba(157, 214, 163, 0.1) 0%, transparent 50%); }
.garden-stage-2 { background-image: radial-gradient(ellipse at 30% 80%, rgba(157, 214, 163, 0.1) 0%, transparent 50%), radial-gradient(circle at 70% 70%, rgba(196, 168, 224, 0.08) 0%, transparent 30%); }
/* Stages 3-9: progressively richer gradients — detailed in design phase */

.gucci-home > *:not(.garden) {
  position: relative;
  z-index: 1;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
  max-height: 40vh;
}

.habit-row {
  display: flex;
  gap: 8px;
  justify-content: center;
  padding: 8px 16px;
  flex-wrap: wrap;
}

.habit-chip {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--text-hint);
  background: var(--bg-card);
  color: var(--text);
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.habit-chip.done {
  background: var(--accent-soft);
  border-color: var(--accent);
}

.chat-input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-card);
  border-radius: 24px;
  margin: 8px 16px;
  box-shadow: var(--shadow);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text);
  font-size: 15px;
  font-family: inherit;
  outline: none;
}

.chat-input::placeholder {
  color: var(--text-hint);
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: var(--accent);
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.send-btn:active {
  transform: scale(0.9);
}

.send-btn:disabled {
  opacity: 0.5;
}
```

- [ ] **Step 4: Verify Gucci Home renders**

Open http://localhost:5173 — should see Gucci emoji, mood bubbles, habits, chat input.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/GucciHome.* frontend/src/components/Gucci.*
git commit -m "feat: Gucci Home page with garden, chat, habits, mood picker"
```

- [ ] **Step 6: Commit chunk 3 milestone**

```bash
git add -A
git commit -m "milestone: chunk 3 complete — React setup, themes, NavBar, Gucci Home"
```

---

## Chunk 4: Goals Page, Day Canvas, Me Page, PWA Setup

### Task 19: Goals Page (By Direction + Daily Board)

**Files:**
- Create: `frontend/src/pages/Goals.jsx`
- Create: `frontend/src/pages/Goals.css`
- Create: `frontend/src/components/GoalCard.jsx`
- Create: `frontend/src/components/GoalCard.css`

- [ ] **Step 1: Create `frontend/src/components/GoalCard.jsx`**

```jsx
import { useNavigate } from "react-router-dom";
import "./GoalCard.css";

const directionColors = {
  "#7EB8DA": "career",
  "#9DD6A3": "health",
  "#C4A8E0": "mind",
  "#F0C987": "life",
};

export default function GoalCard({ goal, direction, nextStep }) {
  const navigate = useNavigate();
  const colorClass = directionColors[direction?.color] || "mind";

  return (
    <div
      className={`goal-card goal-${colorClass}`}
      onClick={() => navigate(`/goals/${goal.id}/chat`)}
    >
      <div className="goal-header">
        <span className="goal-icon">{direction?.icon || "🎯"}</span>
        <span className="goal-title">{goal.title}</span>
      </div>
      <div className="goal-progress-bar">
        <div
          className="goal-progress-fill"
          style={{ width: `${goal.progress}%` }}
        />
      </div>
      <div className="goal-next">
        {nextStep ? `→ ${nextStep.title}` : "No steps yet — tap to plan with Gucci"}
      </div>
    </div>
  );
}
```

```css
/* frontend/src/components/GoalCard.css */
.goal-card {
  padding: 16px;
  border-radius: 20px;
  margin: 8px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow);
}

.goal-card:active { transform: scale(0.98); }

.goal-career { background: rgba(126, 184, 218, var(--bubble-fill)); border: 1.5px solid rgba(126, 184, 218, var(--bubble-border)); }
.goal-health { background: rgba(157, 214, 163, var(--bubble-fill)); border: 1.5px solid rgba(157, 214, 163, var(--bubble-border)); }
.goal-mind { background: rgba(196, 168, 224, var(--bubble-fill)); border: 1.5px solid rgba(196, 168, 224, var(--bubble-border)); }
.goal-life { background: rgba(240, 201, 135, var(--bubble-fill)); border: 1.5px solid rgba(240, 201, 135, var(--bubble-border)); }

.goal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.goal-icon { font-size: 20px; }
.goal-title { font-weight: 700; font-size: 15px; }

.goal-progress-bar {
  height: 6px;
  border-radius: 3px;
  background: var(--text-hint);
  margin-bottom: 8px;
  overflow: hidden;
}

.goal-progress-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--accent);
  transition: width 0.5s ease;
}

.goal-next {
  font-size: 13px;
  color: var(--text-muted);
}
```

- [ ] **Step 2: Create `frontend/src/pages/Goals.jsx`**

```jsx
import { useEffect, useState } from "react";
import { fetchJSON } from "../api";
import GoalCard from "../components/GoalCard";
import "./Goals.css";

export default function Goals() {
  const [directions, setDirections] = useState([]);
  const [goals, setGoals] = useState([]);
  const [steps, setSteps] = useState({});
  const [mode, setMode] = useState("direction"); // "direction" | "daily"

  useEffect(() => {
    fetchJSON("/directions").then(setDirections);
    fetchJSON("/goals").then(async (goals) => {
      setGoals(goals);
      const stepsMap = {};
      for (const g of goals) {
        const s = await fetchJSON(`/goals/${g.id}/steps`);
        stepsMap[g.id] = s;
      }
      setSteps(stepsMap);
    });
  }, []);

  const getNextStep = (goalId) => {
    const goalSteps = steps[goalId] || [];
    return goalSteps.find((s) => s.status !== "done");
  };

  const getDirection = (dirId) => directions.find((d) => d.id === dirId);

  return (
    <div className="goals-page">
      <div className="goals-header">
        <h2>Goals</h2>
        <button
          className="mode-toggle"
          onClick={() => setMode(mode === "direction" ? "daily" : "direction")}
        >
          {mode === "direction" ? "📋 All" : "🎯 Dir"}
        </button>
      </div>

      {mode === "direction" ? (
        directions.map((dir) => {
          const dirGoals = goals.filter((g) => g.direction_id === dir.id);
          if (dirGoals.length === 0) return null;
          return (
            <div key={dir.id} className="direction-section">
              <h3 className="direction-title">
                {dir.icon} {dir.name}
              </h3>
              {dirGoals.map((g) => (
                <GoalCard
                  key={g.id}
                  goal={g}
                  direction={dir}
                  nextStep={getNextStep(g.id)}
                />
              ))}
            </div>
          );
        })
      ) : (
        <div className="daily-board">
          {goals.map((g) => {
            const next = getNextStep(g.id);
            if (!next) return null;
            const dir = getDirection(g.direction_id);
            return (
              <GoalCard key={g.id} goal={g} direction={dir} nextStep={next} />
            );
          })}
        </div>
      )}

      {goals.length === 0 && (
        <div className="empty-state">
          <p>No goals yet!</p>
          <p>Talk to Gucci to set your first goal 🐱</p>
        </div>
      )}
    </div>
  );
}
```

```css
/* frontend/src/pages/Goals.css */
.goals-page { padding: 16px 0; }

.goals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  margin-bottom: 16px;
}

.goals-header h2 { font-size: 24px; font-weight: 700; }

.mode-toggle {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--text-hint);
  background: var(--bg-card);
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
}

.direction-section { margin-bottom: 24px; }

.direction-title {
  padding: 0 16px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.empty-state {
  text-align: center;
  padding: 48px 16px;
  color: var(--text-muted);
  font-size: 16px;
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Goals.* frontend/src/components/GoalCard.*
git commit -m "feat: Goals page with direction view and daily board toggle"
```

---

### Task 20: Goal Chat (Sub-Agent View)

**Files:**
- Create: `frontend/src/components/GoalChat.jsx`
- Create: `frontend/src/components/GoalChat.css`

- [ ] **Step 1: Create `frontend/src/components/GoalChat.jsx`**

```jsx
import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchJSON } from "../api";
import useChat from "../hooks/useChat";
import ChatBubble from "./ChatBubble";
import "./GoalChat.css";

export default function GoalChat() {
  const { goalId } = useParams();
  const navigate = useNavigate();
  const [goal, setGoal] = useState(null);
  const [direction, setDirection] = useState(null);
  const { messages, streaming, loadHistory, send } = useChat("goal", goalId);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchJSON("/goals").then((goals) => {
      const g = goals.find((g) => g.id === parseInt(goalId));
      setGoal(g);
      if (g) {
        fetchJSON("/directions").then((dirs) => {
          setDirection(dirs.find((d) => d.id === g.direction_id));
        });
      }
    });
    loadHistory();
  }, [goalId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    send(input);
    setInput("");
  };

  const markStepDone = async () => {
    const steps = await fetchJSON(`/goals/${goalId}/steps`);
    const next = steps.find((s) => s.status !== "done");
    if (next) {
      await fetchJSON(`/goals/${goalId}/steps/${next.id}`, {
        method: "PUT",
        body: JSON.stringify({ status: "done" }),
      });
    }
  };

  if (!goal) return <div className="loading">Loading...</div>;

  return (
    <div className="goal-chat">
      <div className="goal-chat-header" style={{
        borderColor: direction?.color || "var(--accent)"
      }}>
        <button className="back-btn" onClick={() => navigate("/goals")}>←</button>
        <span>{direction?.icon} {goal.title}</span>
      </div>

      <div className="goal-chat-messages">
        {messages.length === 0 && (
          <ChatBubble
            role="gucci"
            content={`Let's work on "${goal.title}". What would you like to focus on?`}
          />
        )}
        {messages.map((m, i) => (
          <ChatBubble
            key={i}
            role={m.role}
            content={m.content}
            streaming={streaming && i === messages.length - 1 && m.role === "gucci"}
          />
        ))}
        <div ref={chatEndRef} />
      </div>

      <div className="goal-chat-input-bar">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask Gucci about this goal..."
        />
        <button className="done-btn" onClick={markStepDone} title="Mark step done">✓</button>
        <button className="send-btn" onClick={handleSend} disabled={streaming}>↑</button>
      </div>
    </div>
  );
}
```

```css
/* frontend/src/components/GoalChat.css */
.goal-chat {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.goal-chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  font-weight: 700;
  border-bottom: 2px solid;
}

.back-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text);
  cursor: pointer;
}

.goal-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.goal-chat-input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-card);
  border-radius: 24px;
  margin: 8px 16px 80px;
  box-shadow: var(--shadow);
}

.done-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1.5px solid var(--color-health);
  background: transparent;
  color: var(--color-health);
  font-size: 16px;
  cursor: pointer;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/GoalChat.*
git commit -m "feat: goal-specific sub-agent chat view"
```

---

### Task 21: Day Canvas Page (Flowing Time Gradient)

**Files:**
- Create: `frontend/src/pages/DayCanvas.jsx`
- Create: `frontend/src/pages/DayCanvas.css`
- Create: `frontend/src/components/TimeBubble.jsx`
- Create: `frontend/src/components/TimeBubble.css`
- Create: `frontend/src/components/BubblePopup.jsx`
- Create: `frontend/src/components/BubblePopup.css`

- [ ] **Step 1: Create TimeBubble + BubblePopup components**

```jsx
// frontend/src/components/TimeBubble.jsx
import { useState } from "react";
import BubblePopup from "./BubblePopup";
import "./TimeBubble.css";

const dirColorMap = {
  "#7EB8DA": "career", "#9DD6A3": "health",
  "#C4A8E0": "mind", "#F0C987": "life",
};

export default function TimeBubble({ block, directionColor, onDone, onChat }) {
  const [showPopup, setShowPopup] = useState(false);
  const colorClass = dirColorMap[directionColor] || "mind";

  // Calculate height based on duration
  const start = parseTime(block.start_time);
  const end = parseTime(block.end_time);
  const durationMin = (end - start) / 60000;
  const height = Math.max(48, durationMin * 1.2); // 1.2px per minute

  return (
    <>
      <div
        className={`time-bubble bubble-${colorClass}`}
        style={{ height: `${height}px` }}
        onClick={() => setShowPopup(true)}
      >
        <span className="bubble-text">{block.title}</span>
      </div>
      {showPopup && (
        <BubblePopup
          block={block}
          onClose={() => setShowPopup(false)}
          onDone={onDone}
          onChat={onChat}
        />
      )}
    </>
  );
}

function parseTime(str) {
  const [h, m] = str.split(":").map(Number);
  return new Date(2026, 0, 1, h, m).getTime();
}
```

```css
/* frontend/src/components/TimeBubble.css */
.time-bubble {
  margin: 4px auto;
  width: 70%;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.time-bubble:active { transform: scale(0.97); }

.bubble-career { background: rgba(126, 184, 218, var(--bubble-fill)); border: 1.5px solid rgba(126, 184, 218, var(--bubble-border)); }
.bubble-health { background: rgba(157, 214, 163, var(--bubble-fill)); border: 1.5px solid rgba(157, 214, 163, var(--bubble-border)); }
.bubble-mind { background: rgba(196, 168, 224, var(--bubble-fill)); border: 1.5px solid rgba(196, 168, 224, var(--bubble-border)); }
.bubble-life { background: rgba(240, 201, 135, var(--bubble-fill)); border: 1.5px solid rgba(240, 201, 135, var(--bubble-border)); }

.bubble-text {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

```jsx
// frontend/src/components/BubblePopup.jsx
import "./BubblePopup.css";

export default function BubblePopup({ block, onClose, onDone, onChat }) {
  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-card" onClick={(e) => e.stopPropagation()}>
        <div className="popup-title">{block.title}</div>
        <div className="popup-time">
          {block.start_time} — {block.end_time}
        </div>
        <div className="popup-actions">
          <button className="popup-btn chat" onClick={() => onChat?.(block)}>
            💬 Talk
          </button>
          <button className="popup-btn done" onClick={() => onDone?.(block)}>
            ✓ Done
          </button>
        </div>
      </div>
    </div>
  );
}
```

```css
/* frontend/src/components/BubblePopup.css */
.popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fadeIn 0.2s ease;
}

.popup-card {
  background: var(--bg-card);
  border-radius: 24px;
  padding: 24px;
  width: 80%;
  max-width: 320px;
  box-shadow: var(--shadow);
}

.popup-title { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
.popup-time { font-size: 14px; color: var(--text-muted); margin-bottom: 20px; }

.popup-actions { display: flex; gap: 12px; }

.popup-btn {
  flex: 1;
  padding: 12px;
  border-radius: 16px;
  border: none;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.popup-btn.chat { background: var(--accent-soft); color: var(--text); }
.popup-btn.done { background: rgba(157, 214, 163, 0.2); color: var(--color-health); }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
```

- [ ] **Step 2: Create `frontend/src/pages/DayCanvas.jsx`**

```jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchJSON } from "../api";
import TimeBubble from "../components/TimeBubble";
import "./DayCanvas.css";

export default function DayCanvas() {
  const [blocks, setBlocks] = useState([]);
  const [directions, setDirections] = useState([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const navigate = useNavigate();

  const dateStr = currentDate.toISOString().split("T")[0];

  useEffect(() => {
    fetchJSON(`/schedule/${dateStr}`).then(setBlocks);
    fetchJSON("/directions").then(setDirections);
  }, [dateStr]);

  const getDirColor = (dirId) => {
    const d = directions.find((d) => d.id === dirId);
    return d?.color || null;
  };

  const handleDone = async (block) => {
    await fetchJSON(`/schedule/${block.id}`, {
      method: "PUT",
      body: JSON.stringify({ status: "done" }),
    });
    setBlocks((prev) =>
      prev.map((b) => (b.id === block.id ? { ...b, status: "done" } : b))
    );
  };

  const handleChat = (block) => {
    if (block.goal_id) navigate(`/goals/${block.goal_id}/chat`);
  };

  const swipe = (delta) => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() + delta);
    setCurrentDate(d);
  };

  const generateSchedule = async () => {
    await fetchJSON("/schedule/generate", {
      method: "POST",
      body: JSON.stringify({ date: dateStr }),
    });
    fetchJSON(`/schedule/${dateStr}`).then(setBlocks);
  };

  // Build hour slots from 5 to 24
  const hours = Array.from({ length: 20 }, (_, i) => i + 5);

  // Group blocks by start hour
  const blocksByHour = {};
  blocks.filter((b) => b.block_type !== "custom").forEach((b) => {
    const hour = parseInt(b.start_time.split(":")[0]);
    if (!blocksByHour[hour]) blocksByHour[hour] = [];
    blocksByHour[hour].push(b);
  });

  const dayName = currentDate.toLocaleDateString("en", { weekday: "long" });
  const monthDay = currentDate.toLocaleDateString("en", { month: "short", day: "numeric" });

  return (
    <div className="day-canvas">
      <div className="day-header">
        <button className="swipe-btn" onClick={() => swipe(-1)}>◀</button>
        <span className="day-title">{dayName} · {monthDay}</span>
        <button className="swipe-btn" onClick={() => swipe(1)}>▶</button>
      </div>

      <div className="time-flow">
        {hours.map((hour) => {
          const hourBlocks = blocksByHour[hour] || [];
          const isBusy = hourBlocks.length > 0;
          const timeOfDay = hour < 10 ? "morning" : hour < 16 ? "midday" : "evening";

          return (
            <div key={hour} className={`hour-slot ${timeOfDay} ${isBusy ? "busy" : "free"}`}>
              <span className="hour-hint">{hour}</span>
              <div className="hour-content">
                {hourBlocks.map((b) => (
                  <TimeBubble
                    key={b.id}
                    block={b}
                    directionColor={getDirColor(b.direction_id)}
                    onDone={handleDone}
                    onChat={handleChat}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {blocks.length === 0 && (
        <div className="empty-day">
          <button className="generate-btn" onClick={generateSchedule}>
            🔮 Ask Gucci to plan this day
          </button>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Create `frontend/src/pages/DayCanvas.css`**

```css
.day-canvas { padding: 0; }

.day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  position: sticky;
  top: 0;
  background: var(--bg);
  z-index: 10;
}

.day-title { font-size: 18px; font-weight: 700; }
.swipe-btn { background: none; border: none; font-size: 16px; color: var(--text-muted); cursor: pointer; padding: 8px; }

.time-flow {
  display: flex;
  flex-direction: column;
}

.hour-slot {
  display: flex;
  min-height: 40px;
  padding: 4px 0;
  transition: background 0.5s ease;
}

/* Time-of-day gradient tints */
.hour-slot.morning { background: var(--day-morning); }
.hour-slot.midday { background: var(--day-midday); }
.hour-slot.evening { background: var(--day-evening); }

/* Busy zones get slightly darker */
.hour-slot.busy { background-color: var(--day-busy); }

/* Free zones get more contrast (lighter) — achieved by NOT adding busy tint */

.hour-hint {
  width: 28px;
  text-align: right;
  padding-right: 8px;
  font-size: 11px;
  color: var(--text-hint);
  padding-top: 4px;
  flex-shrink: 0;
}

.hour-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.empty-day {
  display: flex;
  justify-content: center;
  padding: 48px 16px;
}

.generate-btn {
  padding: 16px 24px;
  border-radius: 24px;
  border: 1.5px dashed var(--accent);
  background: var(--accent-soft);
  color: var(--text);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.generate-btn:active { transform: scale(0.95); }
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/DayCanvas.* frontend/src/components/TimeBubble.* frontend/src/components/BubblePopup.*
git commit -m "feat: Day Canvas page with flowing time gradient and task bubbles"
```

---

### Task 22: Me Page (Stats + Settings)

**Files:**
- Create: `frontend/src/pages/Me.jsx`
- Create: `frontend/src/pages/Me.css`

- [ ] **Step 1: Create `frontend/src/pages/Me.jsx`**

```jsx
import { useEffect, useState } from "react";
import { fetchJSON } from "../api";
import "./Me.css";

const moodEmojis = { 1: "😔", 2: "😕", 3: "😐", 4: "🙂", 5: "😊" };

export default function Me({ theme, setTheme }) {
  const [settings, setSettings] = useState({});
  const [moods, setMoods] = useState([]);
  const [pet, setPet] = useState({});
  const [apiKey, setApiKey] = useState("");

  useEffect(() => {
    fetchJSON("/settings").then((s) => {
      setSettings(s);
      setApiKey(s.api_key || "");
    });
    fetchJSON("/mood?days=7").then(setMoods);
    fetchJSON("/pet").then(setPet);
  }, []);

  const updateSetting = async (key, value) => {
    await fetchJSON("/settings", {
      method: "PUT",
      body: JSON.stringify({ [key]: value }),
    });
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const saveApiKey = () => updateSetting("api_key", apiKey);

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    updateSetting("theme", next);
  };

  const toggleLang = () => {
    const next = settings.language === "ru" ? "en" : "ru";
    updateSetting("language", next);
  };

  // Mood trend
  const avgMood = moods.length
    ? (moods.reduce((s, m) => s + m.mood, 0) / moods.length).toFixed(1)
    : "-";

  return (
    <div className="me-page">
      <h2>This Week</h2>

      {/* Mood heatmap */}
      <div className="mood-heatmap">
        {["M", "T", "W", "T", "F", "S", "S"].map((day, i) => {
          const mood = moods[i];
          return (
            <div key={i} className="mood-dot-container">
              <span className="mood-day-label">{day}</span>
              <span className="mood-dot">
                {mood ? moodEmojis[mood.mood] : "⬜"}
              </span>
            </div>
          );
        })}
      </div>

      <div className="stats">
        <div className="stat-card">
          <span className="stat-label">Mood trend</span>
          <span className="stat-value">{avgMood} avg</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Garden</span>
          <span className="stat-value">🌸 Stage {pet.garden_stage || 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">XP</span>
          <span className="stat-value">{pet.xp || 0}</span>
        </div>
      </div>

      <h2>Settings</h2>

      <div className="settings-list">
        <div className="setting-row" onClick={toggleTheme}>
          <span>Theme</span>
          <span className="setting-value">{theme === "dark" ? "🌙 Dark" : "☀️ Light"}</span>
        </div>
        <div className="setting-row" onClick={toggleLang}>
          <span>Language</span>
          <span className="setting-value">{settings.language === "ru" ? "🇷🇺 RU" : "🇬🇧 EN"}</span>
        </div>
        <div className="setting-row">
          <span>Wake time</span>
          <input
            className="setting-input"
            type="time"
            value={settings.wake_time || "07:00"}
            onChange={(e) => updateSetting("wake_time", e.target.value)}
          />
        </div>
        <div className="setting-row api-key-row">
          <span>API Key</span>
          <div className="api-key-input">
            <input
              className="setting-input"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-ant-..."
            />
            <button className="save-btn" onClick={saveApiKey}>Save</button>
          </div>
        </div>
      </div>
    </div>
  );
}
```

```css
/* frontend/src/pages/Me.css */
.me-page { padding: 16px; }

.me-page h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
  margin-top: 24px;
}

.me-page h2:first-child { margin-top: 0; }

.mood-heatmap {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg-card);
  border-radius: 20px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.mood-dot-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.mood-day-label { font-size: 11px; color: var(--text-muted); }
.mood-dot { font-size: 20px; }

.stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  background: var(--bg-card);
  border-radius: 20px;
  box-shadow: var(--shadow);
}

.stat-label { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.stat-value { font-size: 16px; font-weight: 700; }

.settings-list {
  background: var(--bg-card);
  border-radius: 20px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--text-hint);
  cursor: pointer;
}

.setting-row:last-child { border-bottom: none; }

.setting-value { color: var(--text-muted); font-weight: 600; }

.setting-input {
  background: transparent;
  border: 1px solid var(--text-hint);
  border-radius: 12px;
  padding: 8px 12px;
  color: var(--text);
  font-family: inherit;
  font-size: 14px;
}

.api-key-row { flex-direction: column; align-items: stretch; gap: 8px; }

.api-key-input { display: flex; gap: 8px; }
.api-key-input .setting-input { flex: 1; }

.save-btn {
  padding: 8px 16px;
  border-radius: 12px;
  border: none;
  background: var(--accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/Me.*
git commit -m "feat: Me page with mood heatmap, stats, and settings"
```

---

### Task 23: PWA Setup (Service Worker + Manifest)

**Files:**
- Create: `frontend/public/manifest.json`
- Create: `frontend/src/sw.js`
- Modify: `frontend/index.html` (add manifest link)
- Modify: `frontend/src/main.jsx` (register SW)

- [ ] **Step 1: Create `frontend/public/manifest.json`**

```json
{
  "name": "MishaGo",
  "short_name": "MishaGo",
  "description": "Your spirit companion on the path",
  "start_url": "/",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#1A1520",
  "theme_color": "#1A1520",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

- [ ] **Step 2: Add manifest link to `frontend/index.html`**

Add in `<head>`:
```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#1A1520" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<link rel="apple-touch-icon" href="/icon-192.png" />
```

- [ ] **Step 3: Register service worker in `frontend/src/main.jsx`**

Add at the end:
```javascript
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(console.error);
  });
}
```

- [ ] **Step 4: Create `frontend/public/sw.js`** (basic cache-first for assets)

```javascript
const CACHE_NAME = "mishago-v1";
const STATIC_ASSETS = ["/", "/index.html"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Network-first for API calls
  if (url.pathname.startsWith("/api")) {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(JSON.stringify({ error: "offline" }), {
          headers: { "Content-Type": "application/json" },
        })
      )
    );
    return;
  }

  // Cache-first for static assets
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
```

- [ ] **Step 5: Create placeholder icons**

```bash
cd "D:\Pet-projects\MishaGo\frontend\public"
# Create simple placeholder PNGs (will be replaced with real Gucci art later)
# For now, use any 192x192 and 512x512 PNG
```

- [ ] **Step 6: Verify PWA installs on Android**

Open in Chrome on Android → should see "Add to Home Screen" prompt.

- [ ] **Step 7: Commit**

```bash
git add frontend/public/ frontend/src/main.jsx frontend/index.html
git commit -m "feat: PWA setup with manifest and service worker"
```

- [ ] **Step 8: Final chunk 4 milestone**

```bash
git add -A
git commit -m "milestone: chunk 4 complete — all frontend pages + PWA setup"
```

---

## Summary

| Chunk | Tasks | What it builds |
|---|---|---|
| 1 | 1-7 | Backend CRUD APIs (settings, pet, habits, goals, mood, schedule) |
| 2 | 8-12 | AI integration (chat SSE, shadow analyzer, onboarding, schedule gen) |
| 3 | 13-18 | React setup, themes, NavBar, chat components, Gucci Home page |
| 4 | 19-23 | Goals page, Day Canvas, Me page, PWA setup |

**Total: 23 tasks, ~200 steps**

After all chunks are complete, the app is a working MVP that can be installed on Android.
