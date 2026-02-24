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

  // Analyze tab state
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [analyzeLoading, setAnalyzeLoading] = useState(false);

  // Threats tab state
  const [threatResult, setThreatResult] = useState(null);
  const [threatLoading, setThreatLoading] = useState(false);

  // Compare tab state
  const [compareApps, setCompareApps] = useState([]);
  const [compareResult, setCompareResult] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);

  // Permissions tab state
  const [permissionsData, setPermissionsData] = useState(null);
  const [permissionsLoading, setPermissionsLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("");

  // Load apps + categories on mount
  useEffect(() => {
    fetchApps();
    fetchCategories();
  }, []);

  async function fetchApps() {
    try {
      const res = await fetch(`${API_BASE}/apps`);
      const data = await res.json();
      setApps(data);
    } catch (err) {
      console.error("Failed to fetch apps:", err);
    }
  }

  async function fetchCategories() {
    try {
      const res = await fetch(`${API_BASE}/permission-categories`);
      const data = await res.json();
      setCategories(data);
    } catch (err) {
      console.error("Failed to fetch categories:", err);
    }
  }

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

  // Analyze tab function
  async function handleAnalyze() {
    if (!selectedApp) return alert("Select an app");
    setAnalyzeLoading(true);
    setAnalyzeResult(null);

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ app_name: selectedApp })
      });

      const data = await res.json();
      if (res.ok) {
        setAnalyzeResult(data);
      } else {
        alert(data.detail || "Analysis failed");
      }
    } catch (err) {
      alert("Analysis failed");
    } finally {
      setAnalyzeLoading(false);
    }
  }

  // Threats tab function
  async function handleDetectThreats() {
    if (!selectedApp) return alert("Select an app");
    setThreatLoading(true);
    setThreatResult(null);

    try {
      const res = await fetch(`${API_BASE}/detect-threats`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ app_name: selectedApp })
      });

      const data = await res.json();
      if (res.ok) {
        setThreatResult(data);
      } else {
        alert(data.detail || "Threat detection failed");
      }
    } catch (err) {
      alert("Threat detection failed");
    } finally {
      setThreatLoading(false);
    }
  }

  // Compare tab functions
  function toggleCompareApp(appName) {
    setCompareApps(prev => {
      if (prev.includes(appName)) {
        return prev.filter(a => a !== appName);
      }
      if (prev.length >= 4) {
        alert("Maximum 4 apps can be compared");
        return prev;
      }
      return [...prev, appName];
    });
  }

  async function handleCompare() {
    if (compareApps.length < 2) return alert("Select at least 2 apps to compare");
    setCompareLoading(true);
    setCompareResult(null);

    try {
      const res = await fetch(`${API_BASE}/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ app_names: compareApps })
      });

      const data = await res.json();
      if (res.ok) {
        setCompareResult(data);
      } else {
        alert(data.detail || "Comparison failed");
      }
    } catch (err) {
      alert("Comparison failed");
    } finally {
      setCompareLoading(false);
    }
  }

  // Permissions tab functions
  async function loadPermissions(category = "") {
    setPermissionsLoading(true);
    try {
      const url = category 
        ? `${API_BASE}/permissions?category=${category}` 
        : `${API_BASE}/permissions`;
      const res = await fetch(url);
      const data = await res.json();
      setPermissionsData(data);
    } catch (err) {
      alert("Failed to load permissions");
    } finally {
      setPermissionsLoading(false);
    }
  }

  useEffect(() => {
    if (activeTab === "permissions") {
      loadPermissions(selectedCategory);
    }
  }, [activeTab, selectedCategory]);

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

      {/* ANALYZE TAB */}
      {activeTab === "analyze" && (
        <div className="dashboard">
          <div className="card">
            <h3>Comprehensive Analysis</h3>
            <p style={{ fontSize: "0.85rem", marginBottom: "1rem", opacity: 0.7 }}>
              Get detailed analysis including permission breakdown, privacy impact, and correlation analysis
            </p>
            <select value={selectedApp} onChange={e => setSelectedApp(e.target.value)}>
              <option value="">Select an app</option>
              {apps.map(app => (
                <option key={app.name} value={app.name}>
                  {app.name}
                </option>
              ))}
            </select>
            <button className="scan-btn" onClick={handleAnalyze}>ANALYZE APP</button>
            {analyzeLoading && <div className="loading">Analyzing...</div>}
          </div>

          {analyzeResult && (
            <div className="card result-card">
              <h3>Comprehensive Analysis — {analyzeResult.app_name}</h3>
              
              <div className="score-section">
                <div className="score-box">
                  <div className="score-value">{analyzeResult.risk_score}</div>
                  <div className="score-label">Risk Score</div>
                </div>
                <div className="score-box">
                  <div className="score-value">{analyzeResult.permission_analysis?.total_declared || analyzeResult.permissions?.length || 0}</div>
                  <div className="score-label">Total Permissions</div>
                </div>
                <div className="score-box">
                  <div className="score-value">{analyzeResult.permission_analysis?.dangerous_count || 0}</div>
                  <div className="score-label">Dangerous</div>
                </div>
              </div>

              <div className={`risk-level ${analyzeResult.risk_level}`}>
                {analyzeResult.risk_level}
              </div>

              {/* Privacy Analysis */}
              {analyzeResult.privacy_analysis && (
                <>
                  <div className="divider" />
                  <h4>Privacy Impact Analysis</h4>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "0.5rem", marginTop: "0.5rem" }}>
                    {Object.entries(analyzeResult.privacy_analysis.privacy_impacts || {}).map(([level, perms]) => (
                      perms.length > 0 && (
                        <div key={level} style={{ 
                          padding: "0.5rem", 
                          background: level === "CRITICAL" ? "rgba(255,0,0,0.2)" : level === "HIGH" ? "rgba(255,165,0,0.2)" : "rgba(75,21,53,0.3)",
                          borderRadius: "8px",
                          fontSize: "0.75rem"
                        }}>
                          <strong>{level}</strong>: {perms.length} permissions
                        </div>
                      )
                    ))}
                  </div>
                </>
              )}

              {/* Threat Indicators */}
              {analyzeResult.threat_indicators && analyzeResult.threat_indicators.detected_threats?.length > 0 && (
                <>
                  <div className="divider" />
                  <h4>Detected Threats</h4>
                  {analyzeResult.threat_indicators.detected_threats.map((threat, i) => (
                    <div key={i} style={{
                      fontSize: "0.82rem",
                      color: "#ff8fab",
                      padding: "0.5rem 0.75rem",
                      background: "rgba(75,21,53,0.3)",
                      borderRadius: "8px",
                      marginTop: "0.5rem",
                      borderLeft: "3px solid #ff8fab"
                    }}>
                      ⚠ {threat}
                    </div>
                  ))}
                </>
              )}

              {/* Risk Assessment */}
              {analyzeResult.risk_assessment?.correlations?.suspicious_patterns?.length > 0 && (
                <>
                  <div className="divider" />
                  <h4>Suspicious Patterns</h4>
                  {analyzeResult.risk_assessment.correlations.suspicious_patterns.map((pattern, i) => (
                    <div key={i} style={{
                      fontSize: "0.82rem",
                      color: "rgba(243,200,221,0.8)",
                      padding: "0.5rem 0.75rem",
                      background: "rgba(75,21,53,0.3)",
                      borderRadius: "8px",
                      marginTop: "0.5rem",
                      borderLeft: "3px solid #D183A9"
                    }}>
                      {pattern}
                    </div>
                  ))}
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* THREATS TAB */}
      {activeTab === "threats" && (
        <div className="dashboard">
          <div className="card">
            <h3>Threat Detection</h3>
            <p style={{ fontSize: "0.85rem", marginBottom: "1rem", opacity: 0.7 }}>
              Detect specific threat indicators and suspicious patterns
            </p>
            <select value={selectedApp} onChange={e => setSelectedApp(e.target.value)}>
              <option value="">Select an app</option>
              {apps.map(app => (
                <option key={app.name} value={app.name}>
                  {app.name}
                </option>
              ))}
            </select>
            <button className="scan-btn" onClick={handleDetectThreats}>DETECT THREATS</button>
            {threatLoading && <div className="loading">Scanning for threats...</div>}
          </div>

          {threatResult && (
            <div className="card result-card">
              <h3>Threat Analysis — {threatResult.app_name}</h3>
              
              <div className="score-section">
                <div className="score-box">
                  <div className="score-value">{threatResult.risk_score}</div>
                  <div className="score-label">Risk Score</div>
                </div>
                <div className="score-box">
                  <div className="score-value">{threatResult.permissions?.length || 0}</div>
                  <div className="score-label">Permissions</div>
                </div>
                <div className="score-box">
                  <div className="score-value">{threatResult.pattern_risk_level}</div>
                  <div className="score-label">Pattern Risk</div>
                </div>
              </div>

              <div className={`risk-level ${threatResult.risk_level || threatResult.pattern_risk_level}`}>
                {threatResult.risk_level || threatResult.pattern_risk_level}
              </div>

              {/* Threat Indicators */}
              {threatResult.threat_indicators && (
                <>
                  <div className="divider" />
                  <h4>Threat Indicators</h4>
                  <div style={{ display: "grid", gap: "0.5rem", marginTop: "0.5rem" }}>
                    <div style={{ padding: "0.5rem", background: "rgba(75,21,53,0.3)", borderRadius: "8px", fontSize: "0.8rem" }}>
                      <strong>Data Exfiltration Risk:</strong> {threatResult.threat_indicators.data_exfiltration_risk}
                    </div>
                    <div style={{ padding: "0.5rem", background: "rgba(75,21,53,0.3)", borderRadius: "8px", fontSize: "0.8rem" }}>
                      <strong>Financial Risk:</strong> {threatResult.threat_indicators.financial_risk}
                    </div>
                    <div style={{ padding: "0.5rem", background: "rgba(75,21,53,0.3)", borderRadius: "8px", fontSize: "0.8rem" }}>
                      <strong>Privacy Risk:</strong> {threatResult.threat_indicators.privacy_risk}
                    </div>
                    <div style={{ padding: "0.5rem", background: "rgba(75,21,53,0.3)", borderRadius: "8px", fontSize: "0.8rem" }}>
                      <strong>Privilege Escalation:</strong> {threatResult.threat_indicators.privilege_escalation ? "YES" : "No"}
                    </div>
                  </div>
                </>
              )}

              {/* Suspicious Patterns */}
              {threatResult.suspicious_patterns && threatResult.suspicious_patterns.length > 0 && (
                <>
                  <div className="divider" />
                  <h4>Suspicious Patterns Detected</h4>
                  {threatResult.suspicious_patterns.map((pattern, i) => (
                    <div key={i} style={{
                      fontSize: "0.82rem",
                      color: "#ff8fab",
                      padding: "0.5rem 0.75rem",
                      background: "rgba(75,21,53,0.3)",
                      borderRadius: "8px",
                      marginTop: "0.5rem",
                      borderLeft: "3px solid #ff8fab"
                    }}>
                      ⚠ {pattern}
                    </div>
                  ))}
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* COMPARE TAB */}
      {activeTab === "compare" && (
        <div className="dashboard">
          <div className="card">
            <h3>Compare Apps</h3>
            <p style={{ fontSize: "0.85rem", marginBottom: "1rem", opacity: 0.7 }}>
              Select 2-4 apps to compare their risk profiles
            </p>
            
            <div style={{ marginBottom: "1rem" }}>
              <p style={{ fontSize: "0.8rem", marginBottom: "0.5rem" }}>Selected apps ({compareApps.length}):</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {compareApps.map(app => (
                  <span key={app} style={{
                    padding: "0.3rem 0.6rem",
                    background: "rgba(211, 131, 169, 0.3)",
                    borderRadius: "15px",
                    fontSize: "0.8rem"
                  }}>
                    {app}
                  </span>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: "1rem" }}>
              <p style={{ fontSize: "0.8rem", marginBottom: "0.5rem" }}>Available apps:</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", maxHeight: "150px", overflowY: "auto" }}>
                {apps.map(app => (
                  <button
                    key={app.name}
                    onClick={() => toggleCompareApp(app.name)}
                    style={{
                      padding: "0.4rem 0.8rem",
                      background: compareApps.includes(app.name) ? "rgba(211, 131, 169, 0.5)" : "rgba(75,21,53,0.3)",
                      border: "1px solid rgba(211, 131, 169, 0.5)",
                      borderRadius: "8px",
                      color: "rgba(243,200,221,0.9)",
                      cursor: "pointer",
                      fontSize: "0.75rem"
                    }}
                  >
                    {app.name}
                  </button>
                ))}
              </div>
            </div>

            <button 
              className="scan-btn" 
              onClick={handleCompare}
              disabled={compareApps.length < 2}
              style={{ opacity: compareApps.length < 2 ? 0.5 : 1 }}
            >
              COMPARE APPS
            </button>
            {compareLoading && <div className="loading">Comparing...</div>}
          </div>

          {compareResult && (
            <div className="card result-card">
              <h3>Comparison Results</h3>
              
              <div style={{ marginBottom: "1rem", padding: "0.5rem", background: "rgba(75,21,53,0.3)", borderRadius: "8px" }}>
                <strong>Highest Risk:</strong> {compareResult.highest_risk} | 
                <strong> Lowest Risk:</strong> {compareResult.lowest_risk}
              </div>

              <div style={{ display: "grid", gap: "0.75rem" }}>
                {compareResult.comparison.map((app, i) => (
                  <div key={i} style={{
                    padding: "1rem",
                    background: "rgba(75,21,53,0.3)",
                    borderRadius: "8px",
                    borderLeft: `4px solid ${
                      app.risk_level === "CRITICAL" ? "#ff4444" : 
                      app.risk_level === "HIGH" ? "#ff8844" : 
                      app.risk_level === "MEDIUM" ? "#ffcc44" : "#44ff88"
                    }`
                  }}>
                    <h4 style={{ margin: "0 0 0.5rem 0" }}>{app.app_name}</h4>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "0.5rem", fontSize: "0.8rem" }}>
                      <div>Risk Score: <strong>{app.risk_score}</strong></div>
                      <div>Permissions: <strong>{app.permission_count}</strong></div>
                      <div>Dangerous: <strong>{app.dangerous_count}</strong></div>
                      <div>Level: <strong className={app.risk_level}>{app.risk_level}</strong></div>
                    </div>
                    {app.critical_permissions?.length > 0 && (
                      <div style={{ marginTop: "0.5rem", fontSize: "0.75rem" }}>
                        <strong>Critical:</strong> {app.critical_permissions.map(p => p.permission).join(", ")}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* PERMISSIONS TAB */}
      {activeTab === "permissions" && (
        <div className="dashboard">
          <div className="card">
            <h3>Permission Database</h3>
            <p style={{ fontSize: "0.85rem", marginBottom: "1rem", opacity: 0.7 }}>
              View all tracked Android permissions and their risk levels
            </p>
            
            <div style={{ marginBottom: "1rem" }}>
              <label style={{ fontSize: "0.8rem", marginRight: "0.5rem" }}>Filter by category:</label>
              <select 
                value={selectedCategory} 
                onChange={e => setSelectedCategory(e.target.value)}
                style={{ padding: "0.4rem", borderRadius: "4px", background: "rgba(75,21,53,0.5)", color: "white", border: "1px solid rgba(211, 131, 169, 0.5)" }}
              >
                <option value="">All Categories</option>
                {categories && Object.entries(categories).map(([key, val]) => (
                  <option key={key} value={key}>{val.name || key}</option>
                ))}
              </select>
            </div>

            {permissionsLoading && <div className="loading">Loading permissions...</div>}
          </div>

          {permissionsData && permissionsData.permissions && (
            <div className="card result-card">
              <h3>
                {permissionsData.category ? `${categories[permissionsData.category]?.name || permissionsData.category} Permissions` : "All Permissions"}
                <span style={{ fontSize: "0.8rem", opacity: 0.6, marginLeft: "0.5rem" }}>
                  ({Object.keys(permissionsData.permissions).length} permissions)
                </span>
              </h3>

              <div style={{ display: "grid", gap: "0.5rem", maxHeight: "400px", overflowY: "auto" }}>
                {Object.entries(permissionsData.permissions).map(([permName, permData]) => (
                  <div key={permName} style={{
                    padding: "0.75rem",
                    background: "rgba(75,21,53,0.3)",
                    borderRadius: "8px",
                    borderLeft: `3px solid ${
                      permData.risk_level === "CRITICAL" ? "#ff4444" : 
                      permData.risk_level === "DANGEROUS" ? "#ff8844" : 
                      permData.risk_level === "HIGH" ? "#ffcc44" : "#44ff88"
                    }`
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <strong style={{ color: "#D183A9" }}>{permName}</strong>
                      <span className={permData.risk_level} style={{ fontSize: "0.7rem", padding: "0.2rem 0.5rem", borderRadius: "4px" }}>
                        {permData.risk_level}
                      </span>
                    </div>
                    <p style={{ fontSize: "0.75rem", margin: "0.3rem 0", opacity: 0.8 }}>{permData.description}</p>
                    <div style={{ fontSize: "0.7rem", opacity: 0.6 }}>
                      Category: {permData.category} | Privacy Impact: {permData.privacy_impact}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
