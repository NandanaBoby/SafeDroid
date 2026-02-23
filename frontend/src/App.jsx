import { useEffect, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [activeTab, setActiveTab] = useState("scan");
  const [apps, setApps] = useState([]);
  const [categories, setCategories] = useState({});

  const [selectedApp, setSelectedApp] = useState("");
  const [scanResult, setScanResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Search bar state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResult, setSearchResult] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);

  // Load apps + categories on mount
  useEffect(() => {
    fetch(`${API_BASE}/apps`)
      .then(res => res.json())
      .then(setApps);

    fetch(`${API_BASE}/permission-categories`)
      .then(res => res.json())
      .then(setCategories);
  }, []);

  async function quickScan() {
    if (!selectedApp) return alert("Select an app");
    setLoading(true);
    setScanResult(null);

    try {
      const res = await fetch(`${API_BASE}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ app_name: selectedApp })
      });

      const data = await res.json();
      setScanResult(data);
    } catch (err) {
      alert("Scan failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    setSearchResult(null);

    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery.trim() })
      });

      const data = await res.json();

      if (!res.ok) {
        setSearchResult({ error: data.detail || "App not found in database." });
        return;
      }

      setSearchResult(data);
    } catch (err) {
      setSearchResult({ error: "Search failed. Make sure the backend is running." });
    } finally {
      setSearchLoading(false);
    }
  }

  function handleSearchKeyDown(e) {
    if (e.key === "Enter") handleSearch();
  }

  return (
    <div className="container">
      <header className="header">
        <h1>SafeDroid</h1>
        <p>Advanced App Permission &amp; Security Analysis Platform</p>
      </header>

      {/* Global Search Bar */}
      <div className="search-section">
        <div className="search-wrapper">
          <span className="search-icon">🔍</span>
          <input
            className="search-input"
            type="text"
            placeholder="Search an app by name or paste a Play Store link..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={handleSearchKeyDown}
          />
          <button className="search-btn" onClick={handleSearch}>
            SEARCH
          </button>
        </div>
        <p className="search-hint">
          Tip: Paste a Google Play link (e.g. https://play.google.com/store/apps/details?id=com.whatsapp) or just type an app name.
        </p>

        {searchLoading && <div className="loading" style={{ marginTop: "1rem" }}>Searching...</div>}

        {searchResult && !searchResult.error && (
          <div className="card" style={{ marginTop: "1rem" }}>
            <h3>Search Result — {searchResult.app_name}</h3>
            {searchResult.resolved_from && searchResult.resolved_from !== searchResult.app_name && (
              <p style={{ fontSize: "0.78rem", color: "rgba(243,200,221,0.5)", marginBottom: "1rem", marginTop: "-0.75rem" }}>
                Resolved from: {searchResult.resolved_from}
              </p>
            )}
            <div className="score-section">
              <div className="score-box">
                <div className="score-value">{searchResult.risk_score}</div>
                <div className="score-label">Risk Score</div>
              </div>
              <div className="score-box">
                <div className="score-value">{searchResult.extracted_permissions?.length ?? "—"}</div>
                <div className="score-label">Permissions</div>
              </div>
              <div className="score-box">
                <div className="score-value">{searchResult.explanations?.length ?? "—"}</div>
                <div className="score-label">Warnings</div>
              </div>
            </div>
            <div className={`risk-level ${searchResult.risk_level}`}>
              {searchResult.risk_level}
            </div>

            {searchResult.explanations?.length > 0 && (
              <>
                <div className="divider" />
                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  {searchResult.explanations.map((exp, i) => (
                    <div key={i} style={{
                      fontSize: "0.82rem",
                      color: "rgba(243,200,221,0.8)",
                      padding: "0.5rem 0.75rem",
                      background: "rgba(75,21,53,0.3)",
                      borderRadius: "8px",
                      borderLeft: "3px solid #D183A9"
                    }}>
                      {exp}
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {searchResult?.error && (
          <div className="card" style={{ marginTop: "1rem" }}>
            <p style={{ color: "#ff8fab", fontSize: "0.9rem" }}>⚠ {searchResult.error}</p>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="tabs">
        {["scan", "analyze", "threats", "compare", "permissions"].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>

      {/* QUICK SCAN */}
      {activeTab === "scan" && (
        <div className="dashboard">
          <div className="card">
            <h3>Quick Risk Scan</h3>
            <select value={selectedApp} onChange={e => setSelectedApp(e.target.value)}>
              <option value="">Select an app</option>
              {apps.map(app => (
                <option key={app.name} value={app.name}>
                  {app.name}
                </option>
              ))}
            </select>
            <button className="scan-btn" onClick={quickScan}>SCAN APP</button>
            {loading && <div className="loading">Analyzing...</div>}
          </div>

          {scanResult && (
            <div className="card result-card">
              <h3>Risk Assessment — {scanResult.app_name}</h3>

              <div className="score-section">
                <div className="score-box">
                  <div className="score-value">{scanResult.risk_score}</div>
                  <div className="score-label">Risk Score</div>
                </div>

                <div className="score-box">
                  <div className="score-value">
                    {scanResult.extracted_permissions.length}
                  </div>
                  <div className="score-label">Permissions</div>
                </div>

                <div className="score-box">
                  <div className="score-value">
                    {scanResult.explanations.length}
                  </div>
                  <div className="score-label">Warnings</div>
                </div>
              </div>

              <div className={`risk-level ${scanResult.risk_level}`}>
                {scanResult.risk_level}
              </div>

              {scanResult.explanations.length > 0 && (
                <>
                  <div className="divider" />
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                    {scanResult.explanations.map((exp, i) => (
                      <div key={i} style={{
                        fontSize: "0.82rem",
                        color: "rgba(243,200,221,0.8)",
                        padding: "0.5rem 0.75rem",
                        background: "rgba(75,21,53,0.3)",
                        borderRadius: "8px",
                        borderLeft: "3px solid #D183A9"
                      }}>
                        {exp}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* PLACEHOLDERS for other tabs */}
      {activeTab !== "scan" && (
        <div className="card placeholder-card">
          <h3>{activeTab.toUpperCase()}</h3>
          <p>This section is wired to backend — logic can be expanded next.</p>
        </div>
      )}
    </div>
  );
}
