import { useEffect, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

// ── Reusable warning row ───────────────────────────────────────────────────────
function WarningRow({ text }) {
  return (
    <div style={{
      fontSize: "0.82rem", color: "rgba(243,200,221,0.85)",
      padding: "0.5rem 0.75rem", background: "rgba(75,21,53,0.35)",
      borderRadius: "8px", borderLeft: "3px solid #D183A9"
    }}>{text}</div>
  );
}

// ── Severity bar ──────────────────────────────────────────────────────────────
function SeverityBar({ label, count, total, color }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div style={{ marginBottom: "0.75rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
        <span style={{ fontSize: "0.8rem", color: "rgba(243,200,221,0.7)", textTransform: "uppercase", letterSpacing: "1px" }}>{label}</span>
        <span style={{ fontSize: "0.8rem", color: color, fontWeight: 700 }}>{count}</span>
      </div>
      <div style={{ height: "6px", background: "rgba(255,255,255,0.08)", borderRadius: "3px", overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, borderRadius: "3px", transition: "width 0.6s ease" }} />
      </div>
    </div>
  );
}

// ── Threat badge ──────────────────────────────────────────────────────────────
function ThreatBadge({ level }) {
  const colors = {
    CRITICAL: { bg: "rgba(255,100,130,0.15)", color: "#ff8fab", border: "rgba(255,100,130,0.4)" },
    HIGH:     { bg: "rgba(209,131,169,0.15)", color: "#D183A9", border: "rgba(209,131,169,0.4)" },
    MEDIUM:   { bg: "rgba(243,200,221,0.1)",  color: "#F3C8DD", border: "rgba(243,200,221,0.3)" },
    LOW:      { bg: "rgba(80,200,120,0.12)",  color: "#6fd99a", border: "rgba(80,200,120,0.3)" },
    true:     { bg: "rgba(255,100,130,0.15)", color: "#ff8fab", border: "rgba(255,100,130,0.4)" },
    false:    { bg: "rgba(80,200,120,0.12)",  color: "#6fd99a", border: "rgba(80,200,120,0.3)" },
  };
  const key = level === true ? "true" : level === false ? "false" : String(level);
  const s = colors[key] || colors.LOW;
  const label = level === true ? "YES" : level === false ? "NO" : level;
  return (
    <span style={{
      padding: "0.25rem 0.75rem", borderRadius: "12px", fontSize: "0.75rem",
      fontWeight: 700, letterSpacing: "1px", fontFamily: "Syne, sans-serif",
      background: s.bg, color: s.color, border: `1px solid ${s.border}`
    }}>{label}</span>
  );
}

export default function App() {
  const [activeTab, setActiveTab]     = useState("scan");
  const [apps, setApps]               = useState([]);
  const [categories, setCategories]   = useState({});

  // ── SCAN state ──────────────────────────────────────────────────────────────
  const [selectedApp, setSelectedApp] = useState("");
  const [scanResult, setScanResult]   = useState(null);
  const [loading, setLoading]         = useState(false);

  // ── SEARCH state ────────────────────────────────────────────────────────────
  const [searchQuery, setSearchQuery]   = useState("");
  const [searchResult, setSearchResult] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);

  // ── ANALYZE state ───────────────────────────────────────────────────────────
  const [analyzeApp, setAnalyzeApp]       = useState("");
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [analyzeLoading, setAnalyzeLoading] = useState(false);

  // ── THREATS state ───────────────────────────────────────────────────────────
  const [threatsApp, setThreatsApp]       = useState("");
  const [threatsResult, setThreatsResult] = useState(null);
  const [threatsLoading, setThreatsLoading] = useState(false);

  // ── COMPARE state ───────────────────────────────────────────────────────────
  const [compareQuery1, setCompareQuery1] = useState("");
  const [compareQuery2, setCompareQuery2] = useState("");
  const [compareResult, setCompareResult] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);

  // ── PERMISSIONS state ────────────────────────────────────────────────────────
  const [allPermissions, setAllPermissions]   = useState({});
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [permsLoading, setPermsLoading]       = useState(false);

  // Load apps + categories on mount
  useEffect(() => {
    fetch(`${API_BASE}/apps`).then(r => r.json()).then(setApps);
    fetch(`${API_BASE}/permission-categories`).then(r => r.json()).then(setCategories);
  }, []);

  // ── SCAN ────────────────────────────────────────────────────────────────────
  async function quickScan() {
    if (!selectedApp) return alert("Select an app");
    setLoading(true); setScanResult(null);
    try {
      const res  = await fetch(`${API_BASE}/scan`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ app_name: selectedApp }) });
      const data = await res.json();
      setScanResult(data);
    } catch { alert("Scan failed"); }
    finally { setLoading(false); }
  }

  // ── SEARCH ──────────────────────────────────────────────────────────────────
  async function handleSearch() {
    if (!searchQuery.trim()) return;
    setSearchLoading(true); setSearchResult(null);
    try {
      const res  = await fetch(`${API_BASE}/search`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: searchQuery.trim() }) });
      const data = await res.json();
      setSearchResult(res.ok ? data : { error: data.detail?.message || data.detail || "App not found." });
    } catch { setSearchResult({ error: "Search failed. Make sure the backend is running." }); }
    finally { setSearchLoading(false); }
  }
  function handleSearchKeyDown(e) { if (e.key === "Enter") handleSearch(); }

  // ── ANALYZE ─────────────────────────────────────────────────────────────────
  async function handleAnalyze() {
    if (!analyzeApp) return alert("Select an app to analyze");
    setAnalyzeLoading(true); setAnalyzeResult(null);
    try {
      const res  = await fetch(`${API_BASE}/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ app_name: analyzeApp }) });
      const data = await res.json();
      setAnalyzeResult(res.ok ? data : { error: data.detail || "Analysis failed." });
    } catch { setAnalyzeResult({ error: "Analysis failed." }); }
    finally { setAnalyzeLoading(false); }
  }

  // ── THREATS ─────────────────────────────────────────────────────────────────
  async function handleThreats() {
    if (!threatsApp) return alert("Select an app");
    setThreatsLoading(true); setThreatsResult(null);
    try {
      const res  = await fetch(`${API_BASE}/detect-threats`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ app_name: threatsApp }) });
      const data = await res.json();
      setThreatsResult(res.ok ? data : { error: data.detail || "Threat detection failed." });
    } catch { setThreatsResult({ error: "Threat detection failed." }); }
    finally { setThreatsLoading(false); }
  }

  // ── COMPARE ─────────────────────────────────────────────────────────────────
  async function handleCompare() {
    if (!compareQuery1.trim() || !compareQuery2.trim()) return alert("Enter two app names or links");
    setCompareLoading(true); setCompareResult(null);

    // Resolve both queries via /search then compare
    try {
      const [r1, r2] = await Promise.all([
        fetch(`${API_BASE}/search`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: compareQuery1.trim() }) }),
        fetch(`${API_BASE}/search`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: compareQuery2.trim() }) })
      ]);
      const [d1, d2] = await Promise.all([r1.json(), r2.json()]);

      if (!r1.ok) { setCompareResult({ error: `App 1: ${d1.detail?.message || d1.detail || "Not found"}` }); return; }
      if (!r2.ok) { setCompareResult({ error: `App 2: ${d2.detail?.message || d2.detail || "Not found"}` }); return; }

      setCompareResult({ app1: d1, app2: d2 });
    } catch { setCompareResult({ error: "Comparison failed." }); }
    finally { setCompareLoading(false); }
  }

  // ── PERMISSIONS ─────────────────────────────────────────────────────────────
  useEffect(() => {
    if (activeTab !== "permissions") return;
    if (Object.keys(allPermissions).length > 0) return; // already loaded
    setPermsLoading(true);
    fetch(`${API_BASE}/permissions`)
      .then(r => r.json())
      .then(data => { setAllPermissions(data); setPermsLoading(false); })
      .catch(() => setPermsLoading(false));
  }, [activeTab]);

  const filteredPermissions = selectedCategory === "ALL"
    ? Object.entries(allPermissions)
    : Object.entries(allPermissions).filter(([, meta]) => meta.category === selectedCategory);

  // ── Shared result card renderer ──────────────────────────────────────────────
  function ScanResultCard({ result, title }) {
    return (
      <div className="card result-card" style={{ marginTop: "1.5rem" }}>
        <h3>{title || `Risk Assessment — ${result.app_name}`}</h3>
        {result.source === "live_fetch" && (
          <p style={{ fontSize: "0.75rem", color: "#6fd99a", marginBottom: "1rem", marginTop: "-0.75rem" }}>
            ✓ Fetched live from Play Store
          </p>
        )}
        <div className="score-section">
          <div className="score-box"><div className="score-value">{result.risk_score}</div><div className="score-label">Risk Score</div></div>
          <div className="score-box"><div className="score-value">{result.extracted_permissions?.length ?? "—"}</div><div className="score-label">Permissions</div></div>
          <div className="score-box"><div className="score-value">{result.explanations?.length ?? "—"}</div><div className="score-label">Warnings</div></div>
        </div>
        <div className={`risk-level ${result.risk_level}`}>{result.risk_level}</div>
        {result.explanations?.length > 0 && (
          <><div className="divider" />
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {result.explanations.map((e, i) => <WarningRow key={i} text={e} />)}
          </div></>
        )}
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <h1>SafeDroid</h1>
        <p>Advanced App Permission &amp; Security Analysis Platform</p>
      </header>

      {/* ── Global Search Bar ── */}
      <div className="search-section">
        <div className="search-wrapper">
          <span className="search-icon">🔍</span>
          <input className="search-input" type="text"
            placeholder="Search an app by name or paste a Play Store link..."
            value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={handleSearchKeyDown}
          />
          <button className="search-btn" onClick={handleSearch}>SEARCH</button>
        </div>
        <p className="search-hint">
          Tip: Paste a Google Play link (e.g. https://play.google.com/store/apps/details?id=com.whatsapp) or just type an app name.
        </p>
        {searchLoading && <div className="loading" style={{ marginTop: "1rem" }}>Searching...</div>}
        {searchResult && !searchResult.error && <ScanResultCard result={searchResult} title={`Search Result — ${searchResult.app_name}`} />}
        {searchResult?.error && (
          <div className="card" style={{ marginTop: "1rem" }}>
            <p style={{ color: "#ff8fab", fontSize: "0.9rem" }}>⚠ {searchResult.error}</p>
          </div>
        )}
      </div>

      {/* ── Tabs ── */}
      <div className="tabs">
        {["scan", "analyze", "threats", "compare", "permissions"].map(tab => (
          <button key={tab} className={`tab-btn ${activeTab === tab ? "active" : ""}`} onClick={() => setActiveTab(tab)}>
            {tab.toUpperCase()}
          </button>
        ))}
      </div>

      {/* ══════════════════════════════════════════════════════════════
          SCAN TAB
      ══════════════════════════════════════════════════════════════ */}
      {activeTab === "scan" && (
        <div className="dashboard">
          <div className="card">
            <h3>Quick Risk Scan</h3>
            <select value={selectedApp} onChange={e => setSelectedApp(e.target.value)}>
              <option value="">Select an app</option>
              {apps.map(app => <option key={app.name} value={app.name}>{app.name}</option>)}
            </select>
            <button className="scan-btn" onClick={quickScan}>SCAN APP</button>
            {loading && <div className="loading">Analyzing...</div>}
          </div>

          {scanResult && (
            <div className="card result-card">
              <h3>Risk Assessment — {scanResult.app_name}</h3>
              <div className="score-section">
                <div className="score-box"><div className="score-value">{scanResult.risk_score}</div><div className="score-label">Risk Score</div></div>
                <div className="score-box"><div className="score-value">{scanResult.extracted_permissions.length}</div><div className="score-label">Permissions</div></div>
                <div className="score-box"><div className="score-value">{scanResult.explanations.length}</div><div className="score-label">Warnings</div></div>
              </div>
              <div className={`risk-level ${scanResult.risk_level}`}>{scanResult.risk_level}</div>
              {scanResult.explanations.length > 0 && (
                <><div className="divider" />
                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  {scanResult.explanations.map((exp, i) => <WarningRow key={i} text={exp} />)}
                </div></>
              )}
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════
          ANALYZE TAB
      ══════════════════════════════════════════════════════════════ */}
      {activeTab === "analyze" && (
        <div>
          <div className="card">
            <h3>Deep Permission Analysis</h3>
            <select value={analyzeApp} onChange={e => setAnalyzeApp(e.target.value)}>
              <option value="">Select an app to analyze</option>
              {apps.map(app => <option key={app.name} value={app.name}>{app.name}</option>)}
            </select>
            <button className="scan-btn" onClick={handleAnalyze}>ANALYZE</button>
            {analyzeLoading && <div className="loading">Running deep analysis...</div>}
          </div>

          {analyzeResult?.error && (
            <div className="card" style={{ marginTop: "1.5rem" }}>
              <p style={{ color: "#ff8fab" }}>⚠ {analyzeResult.error}</p>
            </div>
          )}

          {analyzeResult && !analyzeResult.error && (() => {
            const breakdown = analyzeResult.permission_analysis?.severity_breakdown || {};
            const critical  = breakdown.critical  || [];
            const dangerous = breakdown.dangerous  || [];
            const normal    = breakdown.normal     || [];
            const total     = critical.length + dangerous.length + normal.length;
            const privacy   = analyzeResult.privacy_analysis?.privacy_impacts || {};
            const catScores = analyzeResult.permission_analysis?.category_scores || {};
            const categorized = analyzeResult.categorized_permissions || {};

            return (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", marginTop: "1.5rem" }}>

                {/* Score overview */}
                <div className="card">
                  <h3>Risk Overview</h3>
                  <div className="score-section" style={{ gridTemplateColumns: "1fr 1fr" }}>
                    <div className="score-box"><div className="score-value">{analyzeResult.risk_score}</div><div className="score-label">Risk Score</div></div>
                    <div className="score-box"><div className={`risk-level ${analyzeResult.risk_level}`} style={{ fontSize: "0.9rem" }}>{analyzeResult.risk_level}</div><div className="score-label" style={{ marginTop: "0.5rem" }}>Level</div></div>
                  </div>
                </div>

                {/* Severity breakdown */}
                <div className="card">
                  <h3>Severity Breakdown</h3>
                  <SeverityBar label="Critical"  count={critical.length}  total={total} color="#ff8fab" />
                  <SeverityBar label="Dangerous" count={dangerous.length} total={total} color="#D183A9" />
                  <SeverityBar label="Normal"    count={normal.length}    total={total} color="#6fd99a" />
                </div>

                {/* Privacy impact */}
                <div className="card">
                  <h3>Privacy Impact</h3>
                  {["CRITICAL", "HIGH", "MEDIUM", "LOW"].map(level => {
                    const items = privacy[level] || [];
                    if (!items.length) return null;
                    return (
                      <div key={level} style={{ marginBottom: "1rem" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                          <ThreatBadge level={level} />
                          <span style={{ fontSize: "0.8rem", color: "rgba(243,200,221,0.6)" }}>{items.length} permission{items.length > 1 ? "s" : ""}</span>
                        </div>
                        {items.map((item, i) => (
                          <div key={i} style={{ fontSize: "0.8rem", color: "rgba(243,200,221,0.75)", paddingLeft: "0.5rem", marginBottom: "0.25rem" }}>
                            • {item.permission} — {item.description}
                          </div>
                        ))}
                      </div>
                    );
                  })}
                </div>

                {/* Category scores */}
                <div className="card">
                  <h3>Score by Category</h3>
                  {Object.entries(catScores).sort((a, b) => b[1] - a[1]).map(([cat, score]) => (
                    <div key={cat} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0", borderBottom: "1px solid rgba(243,200,221,0.08)" }}>
                      <span style={{ fontSize: "0.82rem", color: "rgba(243,200,221,0.7)" }}>{cat.replace("_", " ")}</span>
                      <span style={{ fontSize: "0.9rem", fontWeight: 700, color: "#D183A9", fontFamily: "Syne, sans-serif" }}>{score}</span>
                    </div>
                  ))}
                </div>

                {/* Permissions by category — full width */}
                <div className="card" style={{ gridColumn: "1 / -1" }}>
                  <h3>Permissions by Category</h3>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
                    {Object.entries(categorized).map(([catKey, catData]) => (
                      <div key={catKey} style={{ background: "rgba(75,21,53,0.25)", borderRadius: "10px", padding: "1rem", border: "1px solid rgba(243,200,221,0.08)" }}>
                        <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#D183A9", letterSpacing: "1px", marginBottom: "0.75rem", fontFamily: "Syne, sans-serif" }}>
                          {catData.name}
                        </div>
                        {catData.permissions.map((p, i) => (
                          <div key={i} style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", color: "rgba(243,200,221,0.7)", padding: "0.2rem 0" }}>
                            <span>{p.name}</span>
                            <ThreatBadge level={p.risk_level} />
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            );
          })()}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════
          THREATS TAB
      ══════════════════════════════════════════════════════════════ */}
      {activeTab === "threats" && (
        <div>
          <div className="card">
            <h3>Threat Detection</h3>
            <select value={threatsApp} onChange={e => setThreatsApp(e.target.value)}>
              <option value="">Select an app to scan for threats</option>
              {apps.map(app => <option key={app.name} value={app.name}>{app.name}</option>)}
            </select>
            <button className="scan-btn" onClick={handleThreats}>DETECT THREATS</button>
            {threatsLoading && <div className="loading">Scanning for threats...</div>}
          </div>

          {threatsResult?.error && (
            <div className="card" style={{ marginTop: "1.5rem" }}>
              <p style={{ color: "#ff8fab" }}>⚠ {threatsResult.error}</p>
            </div>
          )}

          {threatsResult && !threatsResult.error && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", marginTop: "1.5rem" }}>

              {/* Privilege escalation */}
              <div className="card">
                <h3>Privilege Escalation</h3>
                <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "0.75rem" }}>
                  <ThreatBadge level={threatsResult.threat_indicators?.privilege_escalation} />
                  <span style={{ fontSize: "0.85rem", color: "rgba(243,200,221,0.7)" }}>
                    {threatsResult.threat_indicators?.privilege_escalation
                      ? "DEVICE_ADMIN permission detected — app can control the device"
                      : "No device admin access requested"}
                  </span>
                </div>
                <div style={{ fontSize: "0.8rem", color: "rgba(243,200,221,0.5)", marginTop: "0.5rem" }}>
                  Privilege escalation means an app requests more system access than needed, often used by malware to gain persistent control.
                </div>
              </div>

              {/* Pattern risk level */}
              <div className="card">
                <h3>Overall Pattern Risk</h3>
                <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "0.75rem" }}>
                  <ThreatBadge level={threatsResult.pattern_risk_level} />
                  <span style={{ fontSize: "0.85rem", color: "rgba(243,200,221,0.7)" }}>
                    {threatsResult.pattern_risk_level === "CRITICAL"
                      ? "Suspicious permission combinations detected"
                      : "No suspicious combinations found"}
                  </span>
                </div>
              </div>

              {/* Suspicious patterns — full width */}
              {threatsResult.suspicious_patterns?.length > 0 && (
                <div className="card" style={{ gridColumn: "1 / -1" }}>
                  <h3>Suspicious Permission Combinations</h3>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                    {threatsResult.suspicious_patterns.map((pattern, i) => (
                      <div key={i} style={{
                        display: "flex", alignItems: "flex-start", gap: "0.75rem",
                        padding: "0.75rem", background: "rgba(255,100,130,0.08)",
                        borderRadius: "10px", border: "1px solid rgba(255,100,130,0.2)"
                      }}>
                        <span style={{ fontSize: "1.1rem" }}>⚠</span>
                        <span style={{ fontSize: "0.85rem", color: "rgba(243,200,221,0.9)" }}>{pattern}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {threatsResult.suspicious_patterns?.length === 0 && (
                <div className="card" style={{ gridColumn: "1 / -1" }}>
                  <h3>Suspicious Permission Combinations</h3>
                  <p style={{ color: "#6fd99a", fontSize: "0.9rem" }}>✓ No suspicious permission combinations detected for {threatsResult.app_name}.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════
          COMPARE TAB
      ══════════════════════════════════════════════════════════════ */}
      {activeTab === "compare" && (
        <div>
          <div className="card">
            <h3>Compare Two Apps</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
              <div style={{ position: "relative" }}>
                <span style={{ fontSize: "0.72rem", color: "rgba(243,200,221,0.5)", letterSpacing: "1px", textTransform: "uppercase", display: "block", marginBottom: "0.4rem" }}>App 1</span>
                <input className="search-input" type="text"
                  placeholder="Name or Play Store link..."
                  value={compareQuery1} onChange={e => setCompareQuery1(e.target.value)}
                  style={{ paddingLeft: "1rem" }}
                />
              </div>
              <div>
                <span style={{ fontSize: "0.72rem", color: "rgba(243,200,221,0.5)", letterSpacing: "1px", textTransform: "uppercase", display: "block", marginBottom: "0.4rem" }}>App 2</span>
                <input className="search-input" type="text"
                  placeholder="Name or Play Store link..."
                  value={compareQuery2} onChange={e => setCompareQuery2(e.target.value)}
                  style={{ paddingLeft: "1rem" }}
                />
              </div>
            </div>
            <button className="scan-btn" onClick={handleCompare}>COMPARE</button>
            {compareLoading && <div className="loading">Comparing apps...</div>}
          </div>

          {compareResult?.error && (
            <div className="card" style={{ marginTop: "1.5rem" }}>
              <p style={{ color: "#ff8fab" }}>⚠ {compareResult.error}</p>
            </div>
          )}

          {compareResult && !compareResult.error && (() => {
            const { app1, app2 } = compareResult;
            const winner = app1.risk_score > app2.risk_score ? app1.app_name : app2.app_name;

            return (
              <div style={{ marginTop: "1.5rem" }}>
                {/* Winner banner */}
                <div className="card" style={{ textAlign: "center", marginBottom: "1.5rem", background: "rgba(75,21,53,0.5)", border: "1px solid rgba(255,100,130,0.3)" }}>
                  <div style={{ fontSize: "0.75rem", color: "rgba(243,200,221,0.5)", letterSpacing: "2px", marginBottom: "0.4rem" }}>HIGHER RISK</div>
                  <div style={{ fontFamily: "Syne, sans-serif", fontSize: "1.5rem", fontWeight: 800, color: "#ff8fab" }}>{winner}</div>
                </div>

                {/* Side by side */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
                  {[app1, app2].map((app, idx) => (
                    <div key={idx} className="card">
                      <h3>{app.app_name}</h3>
                      {app.source === "live_fetch" && (
                        <p style={{ fontSize: "0.72rem", color: "#6fd99a", marginBottom: "0.75rem", marginTop: "-0.75rem" }}>✓ Live fetch</p>
                      )}
                      <div className="score-section" style={{ gridTemplateColumns: "1fr 1fr" }}>
                        <div className="score-box"><div className="score-value">{app.risk_score}</div><div className="score-label">Risk Score</div></div>
                        <div className="score-box"><div className="score-value">{app.extracted_permissions?.length}</div><div className="score-label">Permissions</div></div>
                      </div>
                      <div className={`risk-level ${app.risk_level}`} style={{ marginBottom: "1rem" }}>{app.risk_level}</div>
                      <div className="divider" />
                      <div style={{ fontSize: "0.78rem", color: "rgba(243,200,221,0.6)", marginTop: "0.75rem" }}>
                        <strong style={{ color: "rgba(243,200,221,0.85)", display: "block", marginBottom: "0.4rem" }}>Permissions</strong>
                        {app.extracted_permissions?.map((p, i) => (
                          <span key={i} style={{
                            display: "inline-block", margin: "0.2rem", padding: "0.2rem 0.5rem",
                            background: "rgba(75,21,53,0.4)", borderRadius: "6px",
                            border: "1px solid rgba(243,200,221,0.1)", fontSize: "0.72rem"
                          }}>{p}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Score bar comparison */}
                <div className="card" style={{ marginTop: "1.5rem" }}>
                  <h3>Score Comparison</h3>
                  {[app1, app2].map((app, i) => {
                    const maxScore = Math.max(app1.risk_score, app2.risk_score);
                    const pct = maxScore > 0 ? (app.risk_score / maxScore) * 100 : 0;
                    return (
                      <div key={i} style={{ marginBottom: "1rem" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                          <span style={{ fontSize: "0.82rem", color: "rgba(243,200,221,0.8)" }}>{app.app_name}</span>
                          <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "#D183A9", fontFamily: "Syne, sans-serif" }}>{app.risk_score}</span>
                        </div>
                        <div style={{ height: "8px", background: "rgba(255,255,255,0.08)", borderRadius: "4px", overflow: "hidden" }}>
                          <div style={{ width: `${pct}%`, height: "100%", background: "linear-gradient(90deg, #71557A, #D183A9)", borderRadius: "4px", transition: "width 0.8s ease" }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════
          PERMISSIONS TAB
      ══════════════════════════════════════════════════════════════ */}
      {activeTab === "permissions" && (
        <div>
          <div className="card">
            <h3>Permission Database</h3>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              <button
                onClick={() => setSelectedCategory("ALL")}
                style={{
                  padding: "0.4rem 0.9rem", borderRadius: "20px", fontSize: "0.75rem",
                  fontFamily: "Syne, sans-serif", fontWeight: 700, letterSpacing: "1px", cursor: "pointer",
                  background: selectedCategory === "ALL" ? "linear-gradient(135deg, #71557A, #3A345B)" : "transparent",
                  color: selectedCategory === "ALL" ? "#F3C8DD" : "rgba(243,200,221,0.5)",
                  border: `1px solid ${selectedCategory === "ALL" ? "#D183A9" : "rgba(243,200,221,0.15)"}`,
                  transition: "all 0.2s"
                }}>ALL</button>
              {Object.entries(categories).map(([key, cat]) => (
                <button key={key}
                  onClick={() => setSelectedCategory(key)}
                  style={{
                    padding: "0.4rem 0.9rem", borderRadius: "20px", fontSize: "0.75rem",
                    fontFamily: "Syne, sans-serif", fontWeight: 700, letterSpacing: "1px", cursor: "pointer",
                    background: selectedCategory === key ? "linear-gradient(135deg, #71557A, #3A345B)" : "transparent",
                    color: selectedCategory === key ? "#F3C8DD" : "rgba(243,200,221,0.5)",
                    border: `1px solid ${selectedCategory === key ? "#D183A9" : "rgba(243,200,221,0.15)"}`,
                    transition: "all 0.2s"
                  }}>{cat.name}</button>
              ))}
            </div>
          </div>

          {permsLoading && <div className="loading" style={{ marginTop: "1.5rem" }}>Loading permissions...</div>}

          {!permsLoading && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "1rem", marginTop: "1.5rem" }}>
              {filteredPermissions.map(([permName, meta]) => (
                <div key={permName} className="card" style={{ padding: "1.25rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.6rem" }}>
                    <span style={{ fontFamily: "Syne, sans-serif", fontSize: "0.85rem", fontWeight: 700, color: "#F3C8DD" }}>{permName}</span>
                    <ThreatBadge level={meta.risk_level} />
                  </div>
                  <p style={{ fontSize: "0.78rem", color: "rgba(243,200,221,0.65)", marginBottom: "0.6rem", lineHeight: 1.5 }}>{meta.description}</p>
                  <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                    <span style={{ fontSize: "0.7rem", padding: "0.15rem 0.5rem", background: "rgba(58,52,91,0.6)", borderRadius: "6px", color: "rgba(243,200,221,0.5)", border: "1px solid rgba(243,200,221,0.1)" }}>
                      Severity: {meta.severity}/10
                    </span>
                    <span style={{ fontSize: "0.7rem", padding: "0.15rem 0.5rem", background: "rgba(58,52,91,0.6)", borderRadius: "6px", color: "rgba(243,200,221,0.5)", border: "1px solid rgba(243,200,221,0.1)" }}>
                      {meta.category}
                    </span>
                    <span style={{ fontSize: "0.7rem", padding: "0.15rem 0.5rem", background: "rgba(58,52,91,0.6)", borderRadius: "6px", color: "rgba(243,200,221,0.5)", border: "1px solid rgba(243,200,221,0.1)" }}>
                      Privacy: {meta.privacy_impact}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
