import { Component } from "react";

/**
 * Catches React rendering errors anywhere in the subtree.
 * Shows a gentle Gucci-themed fallback instead of a blank page.
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // Log for debugging — non-critical
    console.error("[ErrorBoundary] Caught rendering error:", error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          padding: "32px",
          textAlign: "center",
          fontFamily: "var(--font-body, sans-serif)",
          background: "var(--bg, #1a1a2e)",
          color: "var(--text, #e8e0f0)",
        }}>
          <div style={{ fontSize: "64px", marginBottom: "16px" }}>🌿</div>
          <h2 style={{
            fontSize: "20px",
            fontWeight: 600,
            marginBottom: "8px",
            color: "var(--text, #e8e0f0)",
          }}>
            Gucci is confused...
          </h2>
          <p style={{
            fontSize: "15px",
            color: "var(--text-secondary, #b0a0c8)",
            marginBottom: "28px",
            maxWidth: "280px",
            lineHeight: 1.5,
          }}>
            Something unexpected happened in the garden. Try refreshing the page.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: "10px 28px",
              borderRadius: "24px",
              border: "none",
              background: "linear-gradient(135deg, var(--accent, #9b7dcf), var(--accent-warm, #c4a8e0))",
              color: "white",
              fontSize: "15px",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Refresh
          </button>
          {this.props.showDetails && this.state.error && (
            <details style={{ marginTop: "20px", maxWidth: "360px", fontSize: "12px", opacity: 0.5 }}>
              <summary style={{ cursor: "pointer" }}>Error details</summary>
              <pre style={{ textAlign: "left", whiteSpace: "pre-wrap", marginTop: "8px" }}>
                {this.state.error.toString()}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
