import { useState } from "react";
import { createPortal } from "react-dom";
import BubblePopup from "./BubblePopup";
import "./TimeBubble.css";

const dirColorMap = {
  "#7EB8DA": "career", "#9DD6A3": "health",
  "#C4A8E0": "mind", "#F0C987": "life",
};

export default function TimeBubble({ block, directionColor, onDone, onChat }) {
  const [showPopup, setShowPopup] = useState(false);
  const colorClass = dirColorMap[directionColor] || "mind";

  return (
    <>
      <div
        className={`time-bubble bubble-${colorClass}`}
        onClick={() => setShowPopup(true)}
      >
        <span className="bubble-text">{block.title}</span>
      </div>
      {showPopup && createPortal(
        <BubblePopup
          block={block}
          onClose={() => setShowPopup(false)}
          onDone={(b) => { onDone(b); setShowPopup(false); }}
          onChat={(b) => { onChat(b); setShowPopup(false); }}
        />,
        document.body
      )}
    </>
  );
}
