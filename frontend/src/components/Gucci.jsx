import "./Gucci.css";

const moodColors = {
  happy: "#B89ADB",
  content: "#9ABFDB",
  cozy: "#D4A574",
  sleepy: "#7A8BA0",
  concerned: "#C49A9A",
};

export default function Gucci({ mood = "content", onClick }) {
  const auraColor = moodColors[mood] || moodColors.content;

  return (
    <div className="gucci-wrap" onClick={onClick}>
      {/* Aura rings */}
      <div className="gucci-aura-outer" style={{ "--aura": auraColor }} />
      <div className="gucci-aura-inner" style={{ "--aura": auraColor }} />

      {/* Spirit body */}
      <div className="gucci-spirit">
        <div className="ear ear-left" />
        <div className="ear ear-right" />
        <div className="gucci-face">
          <div className="eye eye-left">
            <div className={`pupil ${mood === "sleepy" ? "sleepy" : ""}`} />
          </div>
          <div className="eye eye-right">
            <div className={`pupil ${mood === "sleepy" ? "sleepy" : ""}`} />
          </div>
          <div className="nose" />
          <div className={`mouth mouth-${mood}`} />
          <div className="whisker wl1" />
          <div className="whisker wl2" />
          <div className="whisker wr1" />
          <div className="whisker wr2" />
        </div>
      </div>

      <span className="gucci-label">Gucci</span>

      {/* Floating particles */}
      <div className="particle p1" />
      <div className="particle p2" />
      <div className="particle p3" />
      <div className="particle p4" />
      <div className="particle p5" />
    </div>
  );
}
