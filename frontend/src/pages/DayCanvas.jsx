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
