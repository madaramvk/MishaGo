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
