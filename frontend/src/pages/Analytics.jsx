import React, { useEffect, useState } from "react";

const API_BASE = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const usd = (n) =>
  n === null || n === undefined ? "—" : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(Number(n));

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    (async () => {
      const res = await fetch(`${API_BASE}/analytics`);
      const j = await res.json();
      setData(j);
    })();
  }, []);

  if (!data) {
    return (
      <section>
        <h1 className="h1">Dataset Analytics</h1>
        <div className="muted">Loading…</div>
      </section>
    );
  }

  const entries = Object.entries(data.avg_price_by_category || {});

  return (
    <section>
      <h1 className="h1">Dataset Analytics</h1>

      <div className="card wide">
        <h2 className="h2">Top Brands</h2>
        <ul className="list">
          {Object.entries(data.top_brands || {}).map(([k, v]) => (
            <li key={k}>
              <strong>{k}</strong> <span className="muted">({v})</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="card wide">
        <h2 className="h2">Average Price by Category</h2>
        {entries.length === 0 ? (
          <div className="muted">No category pricing available.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Category</th>
                <th style={{ textAlign: "right" }}>Avg Price (USD)</th>
              </tr>
            </thead>
            <tbody>
              {entries.map(([cat, avg]) => (
                <tr key={cat}>
                  <td>{cat}</td>
                  <td style={{ textAlign: "right" }}>{usd(avg)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="grid two">
        <div className="card">
          <h2 className="h2">Price Summary</h2>
          <div className="kv">
            {Object.entries(data.price_summary || {}).map(([k, v]) => (
              <div key={k} className="kvrow">
                <span className="key">{k}</span>
                <span className="val">{typeof v === "number" ? usd(v) : String(v)}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h2 className="h2">Missingness</h2>
          <div className="kv">
            {Object.entries(data.missingness || {}).map(([k, v]) => (
              <div key={k} className="kvrow">
                <span className="key">{k}</span>
                <span className="val">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
