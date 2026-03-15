const API_BASE = "http://localhost:5000/api";

export async function fetchJSON(path, options = {}) {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  return resp.json();
}

export function streamSSE(path, onChunk, onDone, onError, onSetupComplete) {
  const source = new EventSource(`${API_BASE}${path}`);
  source.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.done) {
      source.close();
      onDone?.();
    } else if (data.setup_complete) {
      onSetupComplete?.();
    } else if (data.error) {
      source.close();
      onError?.(data.error);
    } else if (data.text) {
      // Strip SETUP_READY line from visible text
      const clean = data.text.replace(/\s*SETUP_READY:.*$/m, '');
      if (clean) onChunk(clean);
    }
  };
  source.onerror = () => {
    source.close();
    onError?.("Connection lost");
  };
  return source;
}
