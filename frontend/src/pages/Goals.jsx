import { useEffect, useState, useCallback } from "react";
import { fetchJSON } from "../api";
import GoalCard from "../components/GoalCard";
import "./Goals.css";

export default function Goals() {
  const [directions, setDirections] = useState([]);
  const [goals, setGoals] = useState([]);
  const [steps, setSteps] = useState({});
  const [mode, setMode] = useState("direction");

  const loadData = useCallback(async () => {
    const dirs = await fetchJSON("/directions");
    setDirections(dirs);
    const goalsData = await fetchJSON("/goals");
    setGoals(goalsData);
    const stepsMap = {};
    for (const g of goalsData) {
      stepsMap[g.id] = await fetchJSON(`/goals/${g.id}/steps`);
    }
    setSteps(stepsMap);
  }, []);

  useEffect(() => { loadData(); }, []);

  const handleStepUpdate = async () => {
    // Reload goals (progress recalculated) and steps
    const goalsData = await fetchJSON("/goals");
    setGoals(goalsData);
    const stepsMap = {};
    for (const g of goalsData) {
      stepsMap[g.id] = await fetchJSON(`/goals/${g.id}/steps`);
    }
    setSteps(stepsMap);
  };

  const getDirection = (dirId) => directions.find((d) => d.id === dirId);

  return (
    <div className="goals-page">
      <div className="goals-header">
        <h2>Goals</h2>
        <button
          className="mode-toggle"
          onClick={() => setMode(mode === "direction" ? "daily" : "direction")}
        >
          {mode === "direction" ? "📋 All" : "🎯 Dir"}
        </button>
      </div>

      {mode === "direction" ? (
        directions.map((dir) => {
          const dirGoals = goals.filter((g) => g.direction_id === dir.id);
          if (dirGoals.length === 0) return null;
          return (
            <div key={dir.id} className="direction-section">
              <h3 className="direction-title">
                {dir.icon} {dir.name}
              </h3>
              {dirGoals.map((g) => (
                <GoalCard
                  key={g.id}
                  goal={g}
                  direction={dir}
                  steps={steps[g.id] || []}
                  onStepUpdate={handleStepUpdate}
                />
              ))}
            </div>
          );
        })
      ) : (
        <div className="daily-board">
          {goals.map((g) => {
            const goalSteps = steps[g.id] || [];
            const hasIncomplete = goalSteps.some((s) => s.status !== "done");
            if (!hasIncomplete) return null;
            const dir = getDirection(g.direction_id);
            return (
              <GoalCard
                key={g.id}
                goal={g}
                direction={dir}
                steps={goalSteps}
                onStepUpdate={handleStepUpdate}
              />
            );
          })}
        </div>
      )}

      {goals.length === 0 && (
        <div className="empty-state">
          <p>No goals yet!</p>
          <p>Talk to Gucci to set your first goal 🐱</p>
        </div>
      )}
    </div>
  );
}
