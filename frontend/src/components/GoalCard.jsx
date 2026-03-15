import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchJSON } from "../api";
import "./GoalCard.css";

const directionColors = {
  "#7EB8DA": "career",
  "#9DD6A3": "health",
  "#C4A8E0": "mind",
  "#F0C987": "life",
};

export default function GoalCard({ goal, direction, steps = [], onStepUpdate }) {
  const [expanded, setExpanded] = useState(false);
  const navigate = useNavigate();
  const colorClass = directionColors[direction?.color] || "mind";
  const nextStep = steps.find((s) => s.status !== "done");
  const doneCount = steps.filter((s) => s.status === "done").length;

  const toggleStep = async (step) => {
    const newStatus = step.status === "done" ? "todo" : "done";
    try {
      await fetchJSON(`/goals/${goal.id}/steps/${step.id}`, {
        method: "PUT",
        body: JSON.stringify({ status: newStatus }),
      });
      onStepUpdate?.();
    } catch (e) {
      console.error("Failed to update step:", e);
    }
  };

  return (
    <div className={`goal-card goal-${colorClass}`}>
      {/* Header — tap to expand/collapse steps */}
      <div className="goal-header" onClick={() => setExpanded(!expanded)}>
        <span className="goal-icon">{direction?.icon || "🎯"}</span>
        <div className="goal-header-text">
          <span className="goal-title">{goal.title}</span>
          <span className="goal-stats">{doneCount}/{steps.length} steps</span>
        </div>
        <span className="goal-chevron">{expanded ? "▾" : "▸"}</span>
      </div>

      {/* Progress bar */}
      <div className="goal-progress-bar">
        <div
          className="goal-progress-fill"
          style={{ width: `${goal.progress}%` }}
        />
      </div>

      {/* Collapsed: show next step */}
      {!expanded && (
        <div className="goal-next">
          {nextStep ? `→ ${nextStep.title}` : "All steps done!"}
        </div>
      )}

      {/* Expanded: show all steps with checkboxes */}
      {expanded && (
        <div className="goal-steps">
          {steps.map((s) => (
            <div
              key={s.id}
              className={`step-row ${s.status === "done" ? "done" : ""}`}
              onClick={() => toggleStep(s)}
            >
              <span className="step-check">
                {s.status === "done" ? "✓" : "○"}
              </span>
              <span className="step-text">{s.title}</span>
            </div>
          ))}
          {steps.length === 0 && (
            <div className="step-empty">No steps yet</div>
          )}

          {/* Chat button */}
          <button
            className="goal-chat-btn"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/goals/${goal.id}/chat`);
            }}
          >
            💬 Discuss with Gucci
          </button>
        </div>
      )}
    </div>
  );
}
