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
