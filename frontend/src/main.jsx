import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Analytics from "./pages/Analytics.jsx";
import "./styles.css";

function Shell({ children }) {
  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">Ikarus Recommender</div>
        <nav className="nav">
          <Link to="/">Recommend</Link>
          <Link to="/analytics">Analytics</Link>
        </nav>
      </header>
      <main className="container">{children}</main>
      <footer className="footer">Built for the Intern Assignment</footer>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Shell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Shell>
    </BrowserRouter>
  </React.StrictMode>
);
