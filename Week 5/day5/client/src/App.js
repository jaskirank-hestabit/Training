import { useEffect, useState, useCallback } from "react";
import "./App.css";

const API = process.env.REACT_APP_BACKEND_URL || "/api";

const STATUS = { idle: "idle", loading: "loading", ok: "ok", error: "error" };

function usePing() {
  const [status, setStatus]     = useState(STATUS.idle);
  const [data, setData]         = useState(null);
  const [error, setError]       = useState(null);
  const [history, setHistory]   = useState([]);
  const [pingCount, setPingCount] = useState(0);

  const ping = useCallback(async () => {
    setStatus(STATUS.loading);
    setError(null);
    const t0 = performance.now();
    try {
      const res  = await fetch(API);
      const ms   = Math.round(performance.now() - t0);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      let body;
      const ct = res.headers.get("content-type") || "";
      body = ct.includes("json") ? await res.json() : await res.text();
      setData(body);
      setStatus(STATUS.ok);
      setPingCount((c) => c + 1);
      setHistory((h) => [
        { ts: new Date().toLocaleTimeString(), ms, host: body?.hostname || "–", ok: true },
        ...h.slice(0, 4),
      ]);
    } catch (e) {
      const ms = Math.round(performance.now() - t0);
      setError(e.message);
      setStatus(STATUS.error);
      setHistory((h) => [
        { ts: new Date().toLocaleTimeString(), ms, host: "–", ok: false },
        ...h.slice(0, 4),
      ]);
    }
  }, []);

  useEffect(() => { ping(); }, [ping]);

  return { status, data, error, history, pingCount, ping };
}

function Dot({ ok }) {
  return <span className={`dot ${ok ? "dot-ok" : "dot-err"}`} />;
}

function Badge({ label, value, accent }) {
  return (
    <div className={`badge ${accent ? "badge-accent" : ""}`}>
      <span className="badge-label">{label}</span>
      <span className="badge-value">{value}</span>
    </div>
  );
}

export default function App() {
  const { status, data, error, history, pingCount, ping } = usePing();

  const connected  = status === STATUS.ok;
  const loading    = status === STATUS.loading;

  return (
    <div className="shell">
      {/* ── header ── */}
      <header className="header">
        <div className="header-left">
          <span className="logo">⬡</span>
          <div>
            <h1 className="title">Production Stack</h1>
            <p className="subtitle">Week 5 · Day 5 · Capstone</p>
          </div>
        </div>
        <div className="header-right">
          <Dot ok={connected} />
          <span className="status-text">
            {loading ? "connecting…" : connected ? "all systems go" : "unreachable"}
          </span>
        </div>
      </header>

      {/* ── stack status row ── */}
      <section className="section">
        <p className="section-label">Stack layers</p>
        <div className="status-row">
          {[
            { name: "HTTPS / TLS",   ok: true,      note: "mkcert cert" },
            { name: "Nginx proxy",   ok: true,      note: "port 8443"   },
            { name: "Load balancer", ok: true,      note: "server1 · server2" },
            { name: "Node API",      ok: connected, note: connected ? "reachable" : error || "…" },
            { name: "MongoDB",       ok: connected, note: "dockerdb"    },
          ].map((s) => (
            <div key={s.name} className={`layer-card ${s.ok ? "" : "layer-card-err"}`}>
              <div className="layer-card-top">
                <Dot ok={s.ok} />
                <span className="layer-name">{s.name}</span>
              </div>
              <span className="layer-note">{s.note}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── main grid ── */}
      <div className="grid">

        {/* left: server response */}
        <section className="card">
          <div className="card-head">
            <span className="card-title">Server response</span>
            <button
              className={`ping-btn ${loading ? "ping-btn-loading" : ""}`}
              onClick={ping}
              disabled={loading}
            >
              {loading ? "pinging…" : "ping /api"}
            </button>
          </div>

          {connected && data && (
            <div className="response-body">
              {typeof data === "object" ? (
                <table className="resp-table">
                  <tbody>
                    {Object.entries(data).map(([k, v]) => (
                      <tr key={k}>
                        <td className="resp-key">{k}</td>
                        <td className="resp-val">
                          {typeof v === "object" ? JSON.stringify(v) : String(v)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <pre className="resp-raw">{String(data)}</pre>
              )}
            </div>
          )}

          {status === STATUS.error && (
            <div className="error-box">
              <span className="error-icon">✕</span> {error}
            </div>
          )}

          {status === STATUS.idle && (
            <p className="muted">Waiting for first ping…</p>
          )}
        </section>

        {/* right: ping history + container info */}
        <div className="right-col">

          {/* load balancer hits */}
          <section className="card">
            <p className="card-title">Load balancer · ping log</p>
            <p className="card-hint">Each ping may hit a different server — watch the hostname</p>
            <div className="ping-history">
              {history.length === 0 && <p className="muted">No pings yet</p>}
              {history.map((h, i) => (
                <div key={i} className={`ping-row ${h.ok ? "" : "ping-row-err"}`}>
                  <Dot ok={h.ok} />
                  <span className="ping-ts">{h.ts}</span>
                  <span className="ping-host">{h.host}</span>
                  <span className="ping-ms">{h.ms} ms</span>
                </div>
              ))}
            </div>
            <div className="ping-count">
              Total pings: <strong>{pingCount}</strong>
            </div>
          </section>

          {/* container info badges */}
          {connected && data && (
            <section className="card">
              <p className="card-title">Container info</p>
              <div className="badge-grid">
                <Badge label="hostname"    value={data.hostname    || "–"} accent />
                <Badge label="PID"         value={data.pid         || "–"} />
                <Badge label="platform"    value={data.platform    || "–"} />
                <Badge label="arch"        value={data.arch        || "–"} />
                <Badge label="node"        value={data.nodeVersion || "–"} />
                <Badge label="uptime"      value={data.uptime      || "–"} />
              </div>
            </section>
          )}

          {/* architecture note */}
          <section className="card card-arch">
            <p className="card-title">Architecture</p>
            <div className="arch-flow">
              {["Browser", "Nginx :8443", "server1 | server2", "MongoDB"].map((n, i, arr) => (
                <span key={n} className="arch-node">
                  {n}{i < arr.length - 1 && <span className="arch-arrow">→</span>}
                </span>
              ))}
            </div>
            <p className="arch-note">
              HTTPS termination at Nginx · round-robin load balancing · compose profiles
            </p>
          </section>

        </div>
      </div>

      <footer className="footer">
        <span>Docker Week 5 · Day 5 Capstone</span>
        <span className="footer-env">NODE_ENV={process.env.NODE_ENV}</span>
      </footer>
    </div>
  );
}