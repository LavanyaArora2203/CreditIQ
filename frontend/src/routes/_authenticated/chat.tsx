import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { LogOut, Send, Download, CheckCircle2, XCircle, Loader2, AlertTriangle } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { streamChat, type ChatEvent } from "@/lib/api-client";

export const Route = createFileRoute("/_authenticated/chat")({
  component: ChatPage,
  ssr: false,
  head: () => ({
    meta: [
      { title: "Chat — CreditIQ" },
      { name: "description", content: "Chat with your AI loan officer." },
    ],
  }),
});

type StageStatus = "running" | "success" | "failed";
type Stage = { stage: string; label: string; status: StageStatus };

type LoanResult = {
  loan_amount: number;
  tenure_months: number;
  interest_rate: number;
  emi: number;
  sanction_letter?: string;
  underwriting_decision?: unknown;
  kyc_verification?: unknown;
};

type Msg =
  | { id: string; role: "user"; content: string }
  | {
      id: string;
      role: "assistant";
      content: string;
      stages?: Stage[];
      result?: LoanResult;
      error?: { stage: string; reason: string };
      streaming?: boolean;
    };

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function formatINR(n: number) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);
}

function ChatPage() {
  const { profile, customerId, token, logout } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: uid(),
      role: "assistant",
      content:
        `Hi${profile?.name ? `, ${profile.name.split(" ")[0]}` : ""}! I'm CreditIQ, your loan officer. ` +
        `Ask me anything about our loan products, or tell me what you'd like to borrow — for example: ` +
        `"I need ₹2,00,000 for 36 months at 12%".`,
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || !token || sending) return;
    setInput("");
    setSending(true);

    const userMsg: Msg = { id: uid(), role: "user", content: text };
    const assistantId = uid();
    const assistantMsg: Msg = {
      id: assistantId,
      role: "assistant",
      content: "",
      stages: [],
      streaming: true,
    };
    setMessages((m) => [...m, userMsg, assistantMsg]);

    const applyAssistant = (updater: (m: Msg & { role: "assistant" }) => Msg) =>
      setMessages((all) =>
        all.map((m) => (m.id === assistantId && m.role === "assistant" ? updater(m) : m)),
      );

    try {
      await streamChat(token, text, (evt: ChatEvent) => {
        if (evt.event === "assistant") {
          applyAssistant((m) => ({
            ...m,
            content: m.content ? `${m.content}\n\n${evt.data.content}` : evt.data.content,
          }));
        } else if (evt.event === "stage") {
          applyAssistant((m) => {
            const stages = m.stages ? [...m.stages] : [];
            const idx = stages.findIndex((s) => s.stage === evt.data.stage);
            const next: Stage = {
              stage: evt.data.stage,
              label: evt.data.label,
              status: evt.data.status,
            };
            if (idx >= 0) stages[idx] = next;
            else stages.push(next);
            return { ...m, stages };
          });
        } else if (evt.event === "result") {
          applyAssistant((m) => ({ ...m, result: evt.data as LoanResult }));
        } else if (evt.event === "error") {
          applyAssistant((m) => {
            const stages = (m.stages || []).map((s) =>
              s.stage === evt.data.stage ? { ...s, status: "failed" as StageStatus } : s,
            );
            return { ...m, stages, error: { stage: evt.data.stage, reason: evt.data.reason } };
          });
        } else if (evt.event === "done") {
          applyAssistant((m) => ({ ...m, streaming: false }));
        }
      });
    } catch (err) {
      applyAssistant((m) => ({
        ...m,
        streaming: false,
        error: {
          stage: "network",
          reason: err instanceof Error ? err.message : "Couldn't reach the loan service.",
        },
      }));
    } finally {
      setSending(false);
    }
  }, [input, token, sending]);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-10 border-b border-border bg-surface/80 backdrop-blur">
        <div className="mx-auto flex w-full max-w-4xl items-center justify-between px-5 py-3">
          <div className="flex items-center gap-2.5">
            <span className="grid h-8 w-8 place-items-center rounded-md bg-primary text-primary-foreground font-display font-bold">
              C
            </span>
            <div className="leading-tight">
              <div className="font-display text-base font-semibold text-foreground">CreditIQ</div>
              <div className="text-xs text-muted-foreground">
                Signed in as <span className="font-medium text-foreground">{profile?.name || customerId}</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => {
              logout();
              navigate({ to: "/login", replace: true });
            }}
            className="inline-flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted"
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign out
          </button>
        </div>
      </header>

      <div ref={scrollerRef} className="flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-5 py-8">
          {messages.map((m) => (
            <MessageBubble key={m.id} msg={m} />
          ))}
        </div>
      </div>

      <footer className="border-t border-border bg-surface/80 backdrop-blur">
        <div className="mx-auto w-full max-w-3xl px-5 py-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void send();
            }}
            className="flex items-end gap-2 rounded-2xl border border-border bg-card p-2 shadow-sm focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/30"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void send();
                }
              }}
              rows={1}
              placeholder="Ask about a loan, or say what you'd like to borrow…"
              className="max-h-40 flex-1 resize-none bg-transparent px-3 py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground"
              disabled={sending}
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="grid h-10 w-10 place-items-center rounded-xl bg-primary text-primary-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Send"
            >
              {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </button>
          </form>
          <p className="mt-2 text-center text-[11px] text-muted-foreground">
            CreditIQ is an AI assistant. Sanction terms are subject to final bank approval.
          </p>
        </div>
      </footer>
    </div>
  );
}

function MessageBubble({ msg }: { msg: Msg }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-sm text-primary-foreground shadow-sm">
          {msg.content}
        </div>
      </div>
    );
  }
  return (
    <div className="flex gap-3">
      <span className="mt-0.5 grid h-7 w-7 flex-none place-items-center rounded-md bg-primary text-primary-foreground font-display text-xs font-bold">
        C
      </span>
      <div className="min-w-0 flex-1 space-y-3">
        {msg.content && (
          <div className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
            {msg.content}
            {msg.streaming && !msg.stages?.length && (
              <span className="ml-1 inline-block h-3 w-1.5 -mb-0.5 animate-shimmer-pulse bg-muted-foreground" />
            )}
          </div>
        )}

        {msg.stages && msg.stages.length > 0 && (
          <div className="rounded-xl border border-border bg-card p-3">
            <div className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Pipeline
            </div>
            <ul className="flex flex-col gap-1.5">
              {msg.stages.map((s) => (
                <li key={s.stage} className="flex items-center gap-2 text-sm">
                  {s.status === "running" && (
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                  )}
                  {s.status === "success" && (
                    <CheckCircle2 className="h-3.5 w-3.5 text-[color:var(--color-success)]" />
                  )}
                  {s.status === "failed" && (
                    <XCircle className="h-3.5 w-3.5 text-destructive" />
                  )}
                  <span
                    className={
                      s.status === "running"
                        ? "text-foreground animate-shimmer-pulse"
                        : s.status === "failed"
                          ? "text-destructive"
                          : "text-muted-foreground"
                    }
                  >
                    {s.label}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {msg.result && <ResultCard result={msg.result} />}

        {msg.error && (
          <div className="rounded-xl border border-destructive/30 bg-destructive/10 p-3">
            <div className="flex items-start gap-2 text-sm text-destructive">
              <AlertTriangle className="mt-0.5 h-4 w-4 flex-none" />
              <div>
                <div className="font-medium">We couldn't complete this step.</div>
                <div className="mt-0.5 text-destructive/90">{msg.error.reason}</div>
                <div className="mt-2 text-xs text-muted-foreground">
                  Feel free to ask about a different amount or tenure — I'm still here.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ResultCard({ result }: { result: LoanResult }) {
  const downloadLetter = () => {
    if (!result.sanction_letter) return;
    const blob = new Blob([result.sanction_letter], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sanction-letter.txt";
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
      <div className="bg-primary px-5 py-4 text-primary-foreground">
        <div className="text-xs uppercase tracking-wider text-primary-foreground/70">Sanctioned</div>
        <div className="mt-1 font-display text-2xl font-semibold">
          {formatINR(result.loan_amount)}
        </div>
      </div>
      <div className="grid grid-cols-3 divide-x divide-border border-b border-border">
        <Stat label="Tenure" value={`${result.tenure_months} mo`} />
        <Stat label="Rate" value={`${result.interest_rate}%`} />
        <Stat label="EMI" value={formatINR(result.emi)} />
      </div>
      {result.sanction_letter && (
        <div className="p-5">
          <div className="mb-2 flex items-center justify-between">
            <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Sanction letter
            </div>
            <button
              onClick={downloadLetter}
              className="inline-flex items-center gap-1.5 rounded-md border border-border bg-background px-2.5 py-1 text-xs font-medium text-foreground hover:bg-muted"
            >
              <Download className="h-3 w-3" />
              Download
            </button>
          </div>
          <pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded-lg bg-muted/50 p-3 text-xs leading-relaxed text-foreground">
            {result.sanction_letter}
          </pre>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="px-4 py-3">
      <div className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="mt-0.5 font-display text-lg font-semibold text-foreground">{value}</div>
    </div>
  );
}
