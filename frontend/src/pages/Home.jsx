import React, { useState } from "react";

const API_BASE = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

function usd(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(n));
}

function CardSkeleton() {
  return (
    <div className="card skeleton">
      <div className="thumb" />
      <div className="line w80" />
      <div className="line w60" />
      <div className="line w95" />
      <div className="price w30" />
    </div>
  );
}

export default function Home() {
  const [prompt, setPrompt] = useState("cozy wooden chair for study table");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function onAsk(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    setItems([]);
    try {
      const res = await fetch(`${API_BASE}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, top_k: 9 })
      });
      if (!res.ok) {
        setErr(`API ${res.status}`);
        return;
      }
      const data = await res.json();
      setItems(Array.isArray(data.items) ? data.items : []);
    } catch (e) {
      setErr(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1 className="h1">Product Recommender</h1>

      <form onSubmit={onAsk} className="search">
        <input
          className="input"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe what you need (e.g., “compact white study desk under $150”)"
        />
        <button className="btn" disabled={loading}>
          {loading ? "Searching…" : "Ask"}
        </button>
      </form>

      {err && <div className="alert">Error: {err}</div>}

      <div className="grid">
        {loading &&
          Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}

        {!loading &&
          items.map((it, i) => {
            const raw = (it.images || "").trim();
            const imgSrc = raw
              ? `${API_BASE}/proxy-image?url=${encodeURIComponent(raw)}`
              : "";

            const link = it.product_url || it.url || "";
            return (
              <article key={i} className="card">
                <img
                  className="thumb"
                  src={imgSrc}
                  alt=""
                  onError={(e) => {
                    e.currentTarget.src =
                      "data:image/svg+xml;utf8," +
                      encodeURIComponent(
                        `<svg xmlns='http://www.w3.org/2000/svg' width='600' height='350'>
                          <rect width='100%' height='100%' fill='#f3f4f6'/>
                          <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle'
                            font-family='Inter, system-ui, sans-serif' font-size='14' fill='#9ca3af'>No image</text>
                         </svg>`
                      );
                  }}
                />
                <div className="meta">
                  <div className="brandline">
                    <span className="brand">{it.brand || "—"}</span>
                    {it.categories && (
                      <span className="chip">{String(it.categories).split(",")[0]}</span>
                    )}
                  </div>
                  <h3 className="title">{it.title}</h3>
                  <p className="desc">{it.gen_description}</p>
                </div>
                <div className="row">
                  <div className="price">{usd(it.price)}</div>
                  {link ? (
                    <a
                      className="btn ghost"
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View product
                    </a>
                  ) : (
                    <span />
                  )}
                </div>
              </article>
            );
          })}
      </div>
    </section>
  );
}
