import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchJSON } from "../api";
import TimeBubble from "../components/TimeBubble";
import "./DayCanvas.css";

// Split day into rows — each row is a flowing timeline segment
const ROWS = [
  { hours: [5, 6, 7, 8, 9, 10], period: "morning", label: "Morning" },
  { hours: [11, 12, 13, 14, 15], period: "midday", label: "Day" },
  { hours: [16, 17, 18, 19, 20], period: "evening", label: "Evening" },
  { hours: [21, 22, 23, 0], period: "night", label: "Night" },
];

export default function DayCanvas() {
  const [blocks, setBlocks] = useState([]);
  const [directions, setDirections] = useState([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const navigate = useNavigate();

  const dateStr = currentDate.toISOString().split("T")[0];

  useEffect(() => {
    fetchJSON(`/schedule/${dateStr}`).then(setBlocks).catch(() => setBlocks([]));
    fetchJSON("/directions").then(setDirections).catch(() => {});
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

  const visibleBlocks = blocks.filter((b) => b.block_type !== "custom");

  // Group blocks by start hour
  const blocksByHour = {};
  visibleBlocks.forEach((b) => {
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

      <div className="timeline-grid">
        {ROWS.map((row) => (
          <div key={row.period} className={`timeline-row ${row.period}`}>
            <div className="row-label">{row.label}</div>
            <div className="row-track">
              <div className="track-line" />
              <div className="track-points">
                {row.hours.map((h) => {
                  const hourBlocks = blocksByHour[h] || [];
                  const isBusy = hourBlocks.length > 0;
                  return (
                    <div key={h} className={`track-point ${isBusy ? "busy" : ""}`}>
                      {isBusy && (
                        <div className="track-bubbles">
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
                      )}
                      <div className="track-dot" />
                      <span className="track-hour">{h === 0 ? "0" : h}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ))}
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
