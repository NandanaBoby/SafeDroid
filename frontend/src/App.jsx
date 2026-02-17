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

  return (
    <div className="container">
      <header className="header">
        <h1>SafeDroid</h1>
        <p>Advanced App Permission & Security Analysis Platform</p>
      </header>

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
            <button onClick={quickScan}>Scan App</button>
            {loading && <div className="loading">Analyzing...</div>}
          </div>

          {scanResult && (
            <div className="card result-card">
              <h3>Risk Assessment</h3>

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
            </div>
          )}
        </div>
      )}

      {/* PLACEHOLDERS for other tabs */}
      {activeTab !== "scan" && (
        <div className="card">
          <h3>{activeTab.toUpperCase()}</h3>
          <p>This section is wired to backend — logic can be expanded next.</p>
        </div>
      )}
    </div>
  );
}
