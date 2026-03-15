import "./ChatBubble.css";

export default function ChatBubble({ role, content, streaming }) {
  return (
    <div className={`chat-bubble ${role}`}>
      <div className={`bubble-content ${streaming ? "streaming" : ""}`}>
        {content}
        {streaming && <span className="cursor">▍</span>}
      </div>
    </div>
  );
}
