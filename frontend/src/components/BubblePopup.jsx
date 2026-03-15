import "./BubblePopup.css";

export default function BubblePopup({ block, onClose, onDone, onChat }) {
  const typeLabels = { habit: "Habit", goal: "Goal task", custom: "Task" };
  const statusLabels = { planned: "Planned", done: "Done ✓", skipped: "Skipped" };

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-card" onClick={(e) => e.stopPropagation()}>
        <div className="popup-type">{typeLabels[block.block_type] || "Task"}</div>
        <div className="popup-title">{block.title}</div>
        <div className="popup-time">{block.start_time} — {block.end_time}</div>
        {block.status !== "planned" && (
          <div className="popup-status">{statusLabels[block.status]}</div>
        )}
        <div className="popup-actions">
          {block.goal_id && (
            <button className="popup-btn chat" onClick={() => onChat?.(block)}>
              💬 Discuss
            </button>
          )}
          {block.status !== "done" && (
            <button className="popup-btn done" onClick={() => onDone?.(block)}>
              ✓ Done
            </button>
          )}
          <button className="popup-btn close" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
