import { useEffect, useState } from "react";
import { fetchJSON } from "../api";
import GoalCard from "../components/GoalCard";
import "./Goals.css";

export default function Goals() {
  const [directions, setDirections] = useState([]);
  const [goals, setGoals] = useState([]);
  const [steps, setSteps] = useState({});
  const [mode, setMode] = useState("direction"); // "direction" | "daily"

  useEffect(() => {
    fetchJSON("/directions").then(setDirections);
    fetchJSON("/goals").then(async (goals) => {
      setGoals(goals);
      const stepsMap = {};
      for (const g of goals) {
        const s = await fetchJSON(`/goals/${g.id}/steps`);
        stepsMap[g.id] = s;
      }
      setSteps(stepsMap);
    });
  }, []);

  const getNextStep = (goalId) => {
    const goalSteps = steps[goalId] || [];
    return goalSteps.find((s) => s.status !== "done");
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
                  nextStep={getNextStep(g.id)}
                />
              ))}
            </div>
          );
        })
      ) : (
        <div className="daily-board">
          {goals.map((g) => {
            const next = getNextStep(g.id);
            if (!next) return null;
            const dir = getDirection(g.direction_id);
            return (
              <GoalCard key={g.id} goal={g} direction={dir} nextStep={next} />
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
