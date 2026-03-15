import { useState, useCallback, useRef } from "react";
import { fetchJSON, streamSSE } from "../api";

export default function useChat(contextType = "general", goalId = null, onSetupComplete = null) {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [loading, setLoading] = useState(false);
  const sourceRef = useRef(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      let path = `/chat/history?context_type=${contextType}&limit=20`;
      if (goalId) path += `&goal_id=${goalId}`;
      const data = await fetchJSON(path);
      setMessages(data);
    } catch (e) {
      console.error("Failed to load chat history:", e);
    }
    setLoading(false);
  }, [contextType, goalId]);

  const send = useCallback((text) => {
    if (!text.trim() || streaming) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setStreaming(true);

    let accumulated = "";
    const path = goalId
      ? `/chat/goal/${goalId}/stream?message=${encodeURIComponent(text)}`
      : `/chat/stream?message=${encodeURIComponent(text)}`;

    setMessages((prev) => [...prev, { role: "gucci", content: "" }]);

    sourceRef.current = streamSSE(
      path,
      (chunk) => {
        accumulated += chunk;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "gucci", content: accumulated };
          return updated;
        });
      },
      () => setStreaming(false),
      (error) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "gucci",
            content: "I'm a bit sleepy right now... try again in a moment? 😴",
          };
          return updated;
        });
        setStreaming(false);
      },
      onSetupComplete
    );
  }, [streaming, goalId, onSetupComplete]);

  const stop = useCallback(() => {
    sourceRef.current?.close();
    setStreaming(false);
  }, []);

  return { messages, streaming, loading, loadHistory, send, stop };
}
