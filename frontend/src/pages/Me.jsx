export default function Me({ theme, setTheme }) {
  return (
    <div style={{ padding: "24px", color: "var(--text)" }}>
      <h2>Me</h2>
      <p style={{ color: "var(--text-muted)", marginTop: "8px" }}>Coming soon...</p>
      <button
        style={{
          marginTop: "16px",
          padding: "8px 16px",
          borderRadius: "20px",
          border: "1.5px solid var(--accent)",
          background: "var(--accent-soft)",
          color: "var(--text)",
          cursor: "pointer",
        }}
        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      >
        Toggle theme (current: {theme})
      </button>
    </div>
  );
}
