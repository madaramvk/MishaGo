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
