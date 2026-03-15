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
