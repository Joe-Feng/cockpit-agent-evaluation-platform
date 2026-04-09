import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "目标总览", hint: "目标健康与告警态势", end: true },
  { to: "/runs", label: "运行中心", hint: "运行状态与结果归一", end: false },
  { to: "/cases", label: "用例回看", hint: "单用例历史回放", end: false },
  { to: "/trends", label: "趋势看板", hint: "通过率漂移与走势", end: false },
  { to: "/regressions", label: "回归中心", hint: "回归队列与告警流", end: false },
];

export function Layout() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand-card brand-card--hero">
          <h1>治理驾驶舱</h1>
          <p className="body-muted">桌面优先的目标健康、漂移与回归控制台。</p>
        </div>

        <nav className="nav-list" aria-label="主导航">
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

        <div className="sidebar-status panel panel--sidebar-status">
          <p className="eyebrow">系统态势</p>
          <div className="sidebar-footer">
            <span className="badge badge--good">分析器就绪</span>
            <span className="badge badge--warm">基线已加载</span>
            <span className="badge">通知待命</span>
          </div>
        </div>
      </aside>

      <div className="workspace">
        <header className="masthead panel panel--masthead">
          <div>
            <p className="eyebrow">运行态势总览</p>
            <h2>目标健康、漂移与回归</h2>
            <p className="body-muted">
              在同一控制台内持续关注套件健康、趋势变化与回归风险。
            </p>
          </div>
          <div className="masthead__chips">
            <span className="badge">统一控制台</span>
            <span className="badge badge--warm">风险可见</span>
            <span className="badge badge--good">桌面工作流</span>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
