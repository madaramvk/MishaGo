import { useParams } from "react-router-dom";

export default function GoalChat() {
  const { goalId } = useParams();
  return (
    <div style={{ padding: "24px", color: "var(--text)" }}>
      <h2>Goal Chat</h2>
      <p style={{ color: "var(--text-muted)", marginTop: "8px" }}>Goal #{goalId} — coming soon...</p>
    </div>
  );
}
