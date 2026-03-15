import { useNavigate } from "react-router-dom";
import "./GoalCard.css";

const directionColors = {
  "#7EB8DA": "career",
  "#9DD6A3": "health",
  "#C4A8E0": "mind",
  "#F0C987": "life",
};

export default function GoalCard({ goal, direction, nextStep }) {
  const navigate = useNavigate();
  const colorClass = directionColors[direction?.color] || "mind";

  return (
    <div
      className={`goal-card goal-${colorClass}`}
      onClick={() => navigate(`/goals/${goal.id}/chat`)}
    >
      <div className="goal-header">
        <span className="goal-icon">{direction?.icon || "🎯"}</span>
        <span className="goal-title">{goal.title}</span>
      </div>
      <div className="goal-progress-bar">
        <div
          className="goal-progress-fill"
          style={{ width: `${goal.progress}%` }}
        />
      </div>
      <div className="goal-next">
        {nextStep ? `→ ${nextStep.title}` : "No steps yet — tap to plan with Gucci"}
      </div>
    </div>
  );
}
