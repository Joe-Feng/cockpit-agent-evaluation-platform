import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Target Overview", hint: "Target health and alert posture", end: true },
  { to: "/runs", label: "Run Center", hint: "Run status and normalized results" },
  { to: "/cases", label: "Case Explorer", hint: "Replay failure history per case" },
  { to: "/trends", label: "Trend Dashboard", hint: "Pass-rate drift and momentum" },
  { to: "/regressions", label: "Regression Center", hint: "Severity queue and alert feed" },
];

export function Layout() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand-card">
          <p className="eyebrow">Phase 3</p>
          <h1>Governance Console</h1>
          <p className="body-muted">
            Dashboard, trends, and alerts for agent evaluation operations.
          </p>
        </div>
        <nav className="nav-list" aria-label="Primary">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              className={({ isActive }) => (isActive ? "nav-link nav-link--active" : "nav-link")}
              end={item.end}
              to={item.to}
            >
              <span className="nav-link__label">{item.label}</span>
              <span className="nav-link__hint">{item.hint}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className="badge badge--good">Analyzer Ready</span>
          <span className="badge">Notifier Standby</span>
        </div>
      </aside>
      <div className="workspace">
        <header className="masthead">
          <div>
            <p className="eyebrow">Agent Evaluation Platform</p>
            <h2>Dashboard, trend monitoring, and alerting</h2>
          </div>
          <div className="masthead__chips">
            <span className="badge">Single control plane</span>
            <span className="badge badge--warm">Baseline-aware</span>
            <span className="badge badge--good">Ops focused</span>
          </div>
        </header>
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
