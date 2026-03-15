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
        {messages.length === 0 && !streaming && (
          <ChatBubble
            role="gucci"
            content={`Как у тебя дела с "${goal.title}"? Расскажи, что думаешь об этом 🐱`}
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
