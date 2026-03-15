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

  // Gucci speaks first on page load
  const greetingSent = useRef(false);
  useEffect(() => {
    if (greetingSent.current || streaming) return;

    fetchJSON("/settings").then((settings) => {
      if (!settings.api_key) return; // no API key yet
      if (greetingSent.current) return;
      greetingSent.current = true;

      if (settings.onboarded !== "true") {
        // First time — Gucci initiates onboarding conversation
        send("Привет! Я только что открыл приложение. Познакомимся?");
      } else if (messages.length === 0) {
        // Returning user with no chat history today
        const hour = new Date().getHours();
        let prompt;
        if (hour < 12) prompt = "Доброе утро! Как я себя чувствую сегодня?";
        else if (hour < 18) prompt = "Привет! Как проходит мой день?";
        else prompt = "Добрый вечер! Как прошёл мой день?";
        send(prompt);
      }
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
