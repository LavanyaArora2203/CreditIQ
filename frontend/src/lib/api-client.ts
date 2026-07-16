// Small typed API client for the loan assistant backend.
// Configure the base URL with VITE_LOAN_API_URL — this must be set to the
// deployed backend's URL in production (e.g. in Vercel's Project Settings
// → Environment Variables, or a `.env` file locally, based on .env.example).

const configuredBase = (import.meta.env.VITE_LOAN_API_URL as string | undefined)?.replace(
  /\/$/,
  "",
);

if (!configuredBase && !import.meta.env.DEV) {
  // Fail loudly at build/runtime in production rather than silently
  // pointing requests at localhost, which would never work when deployed.
  throw new Error(
    "VITE_LOAN_API_URL is not set. Configure it in your deployment environment " +
      "(see .env.example) before building for production.",
  );
}

// Only used for local development when no .env is present.
const DEV_FALLBACK = "http://localhost:9000";

export const API_BASE = configuredBase || DEV_FALLBACK;

export type AuthResponse = { access_token: string; token_type: string; customer_id: string };
export type UserProfile = {
  customer_id: string;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
};

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) msg = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* ignore */
    }
    throw new Error(msg);
  }
  return res.json() as Promise<T>;
}

export const api = {
  signup: (customer_id: string, password: string) =>
    fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer_id, password }),
    }).then(jsonOrThrow<AuthResponse>),

  login: (customer_id: string, password: string) =>
    fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer_id, password }),
    }).then(jsonOrThrow<AuthResponse>),

  me: (token: string) =>
    fetch(`${API_BASE}/me`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(jsonOrThrow<UserProfile>),
};

/** SSE event types the /chat endpoint emits. */
export type ChatEvent =
  | { event: "assistant"; data: { content: string } }
  | {
      event: "stage";
      data: { stage: string; status: "running" | "success" | "failed"; label: string };
    }
  | {
      event: "result";
      data: {
        loan_amount: number;
        tenure_months: number;
        interest_rate: number;
        emi: number;
        underwriting_decision?: unknown;
        kyc_verification?: unknown;
        sanction_letter?: string;
      };
    }
  | { event: "error"; data: { stage: string; reason: string; raw?: unknown } }
  | { event: "done"; data: Record<string, never> };

/**
 * POST /chat and stream SSE events back. We use fetch + ReadableStream
 * because EventSource can't send an Authorization header.
 */
export async function streamChat(
  token: string,
  message: string,
  onEvent: (evt: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ message }),
    signal,
  });
  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Chat request failed (${res.status})`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  const flushEvent = (block: string) => {
    let eventName = "message";
    const dataLines: string[] = [];
    for (const raw of block.split("\n")) {
      if (!raw || raw.startsWith(":")) continue;
      const idx = raw.indexOf(":");
      const field = idx === -1 ? raw : raw.slice(0, idx);
      const value = idx === -1 ? "" : raw.slice(idx + 1).replace(/^ /, "");
      if (field === "event") eventName = value;
      else if (field === "data") dataLines.push(value);
    }
    if (!dataLines.length) return;
    try {
      const data = JSON.parse(dataLines.join("\n"));
      onEvent({ event: eventName, data } as ChatEvent);
    } catch {
      /* ignore malformed */
    }
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let sep;
    while ((sep = buf.indexOf("\n\n")) !== -1) {
      const block = buf.slice(0, sep);
      buf = buf.slice(sep + 2);
      flushEvent(block);
    }
  }
  if (buf.trim()) flushEvent(buf);
}
