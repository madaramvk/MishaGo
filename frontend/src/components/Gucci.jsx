import "./Gucci.css";

const moodColors = {
  happy: "#D4A46C",
  content: "#9EC28D",
  cozy: "#D4A46C",
  sleepy: "#A89880",
  concerned: "#C4A090",
};

export default function Gucci({ mood = "content", onClick }) {
  const auraColor = moodColors[mood] || moodColors.content;

  return (
    <div className="gucci-wrap" onClick={onClick}>
      {/* Background glow so Gucci pops from any background */}
      <div className="gucci-glow" style={{ "--aura": auraColor }} />

      <div className="gucci-character">
        {/* Ears */}
        <div className="ear ear-l">
          <div className="ear-inner" />
        </div>
        <div className="ear ear-r">
          <div className="ear-inner" />
        </div>

        {/* Head */}
        <div className="head">
          {/* Eyes */}
          <div className="eye eye-l">
            <div className={`pupil ${mood === "sleepy" ? "sleepy" : ""}`}>
              <div className="eye-shine" />
            </div>
          </div>
          <div className="eye eye-r">
            <div className={`pupil ${mood === "sleepy" ? "sleepy" : ""}`}>
              <div className="eye-shine" />
            </div>
          </div>

          {/* Nose + mouth */}
          <div className="nose" />
          <div className={`mouth mood-${mood}`} />

          {/* Whiskers */}
          <div className="whisker wl1" />
          <div className="whisker wl2" />
          <div className="whisker wr1" />
          <div className="whisker wr2" />

          {/* Cheek blush */}
          <div className="cheek cheek-l" />
          <div className="cheek cheek-r" />
        </div>

        {/* Body */}
        <div className="body">
          {/* Arms */}
          <div className="arm arm-l" />
          <div className="arm arm-r" />

          {/* Belly mark */}
          <div className="belly" />
        </div>

        {/* Legs/feet */}
        <div className="feet">
          <div className="foot foot-l" />
          <div className="foot foot-r" />
        </div>

        {/* Tail */}
        <div className="tail" />
      </div>

      <span className="gucci-label">Gucci</span>

      {/* Floating particles */}
      <div className="sparkle s1">✦</div>
      <div className="sparkle s2">✧</div>
      <div className="sparkle s3">✦</div>
      <div className="sparkle s4">✧</div>
    </div>
  );
}
