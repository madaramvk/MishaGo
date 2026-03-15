import { useEffect, useState, useRef, useCallback } from "react";
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
  const [xpFloats, setXpFloats] = useState([]);
  const handleSetupComplete = useCallback(() => {
    // Onboarding done — reload everything
    fetchJSON("/pet").then(setPet).catch(console.error);
    fetchJSON("/habits?today=true").then(setHabits).catch(console.error);
  }, []);

  const { messages, streaming, loadHistory, send } = useChat("general", null, handleSetupComplete);
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

  // Gucci speaks first on page load — context-aware, language-aware
  const greetingSent = useRef(false);
  const historyLoaded = useRef(false);

  // Track when history is loaded so we know if today has messages
  useEffect(() => {
    if (messages.length > 0) historyLoaded.current = true;
  }, [messages]);

  useEffect(() => {
    if (greetingSent.current || streaming) return;

    fetchJSON("/settings").then((settings) => {
      if (!settings.api_key) return;
      if (greetingSent.current) return;

      const lang = settings.language || "en";
      const hour = new Date().getHours();

      if (settings.onboarded !== "true") {
        greetingSent.current = true;
        // First-time onboarding prompt — language aware
        if (lang === "ru") {
          send("Привет! Я только что открыл приложение. Давай познакомимся?");
        } else {
          send("Hey, I just opened the app for the first time. Can we get to know each other?");
        }
      } else if (messages.length === 0) {
        // Returning user with no chat today — send time-based greeting with recent context
        greetingSent.current = true;
        let prompt;
        if (lang === "ru") {
          if (hour < 12) prompt = "Доброе утро! Как я себя чувствую сегодня? Что планирую сделать?";
          else if (hour < 18) prompt = "Привет! Как проходит мой день? Удаётся ли выполнять задуманное?";
          else prompt = "Добрый вечер! Как прошёл мой день? Что успел сделать?";
        } else {
          if (hour < 12) prompt = "Good morning! How am I feeling today? What are my plans?";
          else if (hour < 18) prompt = "Hey! How is my day going? Am I keeping up with my plans?";
          else prompt = "Good evening! How did my day go? What did I manage to get done?";
        }
        send(prompt);
      }
      // If messages.length > 0 — user already chatted today, don't auto-greet
    }).catch(() => {});
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
      if (newState) {
        // Optimistically update XP
        setPet((p) => ({ ...p, xp: p.xp + xpReward }));
        // Show floating +XP text
        const floatId = Date.now();
        setXpFloats((prev) => [...prev, { id: floatId, amount: xpReward }]);
        setTimeout(() => setXpFloats((prev) => prev.filter((f) => f.id !== floatId)), 1200);
        // Refresh pet mood from server after a short delay
        setTimeout(() => fetchJSON("/pet").then(setPet).catch(console.error), 600);
      }
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
        {/* Floating XP animations */}
        {xpFloats.map((f) => (
          <span key={f.id} className="xp-float">+{f.amount} XP</span>
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
