"use client";

import { FormEvent, useState } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type QueryResponse = {
  answer: string;
  session_id: string;
};

type ErrorResponse = {
  detail?: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function HomePage() {
  const [draft, setDraft] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState("Ask about products, orders, or order placement.");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setStatus("Contacting Meridian support...");
    setMessages((current) => [...current, { role: "user", content: message }]);
    setDraft("");

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
        }),
      });

      const payload = (await response.json()) as QueryResponse | ErrorResponse;
      if (!response.ok) {
        const errorPayload = payload as ErrorResponse;
        throw new Error(errorPayload.detail ?? "Request failed");
      }

      const successPayload = payload as QueryResponse;
      setSessionId(successPayload.session_id);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: successPayload.answer },
      ]);
      setStatus("Connected to FastAPI + OpenAI Agents SDK + MCP.");
    } catch (error) {
      const messageText =
        error instanceof Error ? error.message : "Something went wrong";
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: `I hit an error reaching the backend: ${messageText}`,
        },
      ]);
      setStatus("Backend request failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="chat-frame">
        <header className="hero">
          <p className="hero-kicker">Meridian Electronics</p>
          <h1>Support that looks up the real order data.</h1>
          <p>
            This UI sends every question to the FastAPI backend, which uses the
            OpenAI Agents SDK and live MCP tools for products, customers, and orders.
          </p>
          <div className="chat-meta">
            <span>Session: {sessionId ?? "new conversation"}</span>
          </div>
        </header>

        <section className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              Ask about stock, order lookup, authentication, or placing an order.
            </div>
          ) : (
            messages.map((message, index) => (
              <article
                className={`message ${message.role}`}
                key={`${message.role}-${index}`}
              >
                <span className="message-label">{message.role}</span>
                {message.content}
              </article>
            ))
          )}
        </section>

        <section className="composer">
          <form onSubmit={handleSubmit}>
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Example: Check whether COM-0006 is in stock, or look up my order."
            />
            <div className="composer-row">
              <div className="status">{status}</div>
              <button className="submit" disabled={isSubmitting} type="submit">
                {isSubmitting ? "Sending..." : "Send message"}
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
}
