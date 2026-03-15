import "./Gucci.css";

const expressions = {
  happy: "😸",
  content: "😺",
  cozy: "😻",
  sleepy: "😴",
  concerned: "🥺",
};

export default function Gucci({ mood = "content", onClick }) {
  return (
    <div className="gucci-container" onClick={onClick}>
      <div className="gucci-aura" />
      <div className="gucci-body">
        <span className="gucci-face">{expressions[mood] || "😺"}</span>
      </div>
      <div className="gucci-name">Gucci</div>
    </div>
  );
}
