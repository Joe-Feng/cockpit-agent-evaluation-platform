import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "工作台", hint: "摘要卡片与主动作入口", end: true },
  { to: "/suites", label: "测试集", hint: "suite、case 与导入工作流", end: false },
  { to: "/runs", label: "运行", hint: "创建、排队与查看执行", end: false },
  { to: "/results", label: "结果", hint: "case 历史与结果追溯", end: false },
  { to: "/risks", label: "风险", hint: "回归与告警处理中心", end: false },
  { to: "/settings", label: "设置", hint: "target、环境与偏好配置", end: false },
];

export function Layout() {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        跳到主内容
      </a>

      <aside className="shell-nav">
        <div className="shell-brand">
          <p className="eyebrow">Cockpit</p>
          <h1>评测驾驶舱</h1>
          <p className="body-muted">面向测试与算法团队的高密度评测工作台。</p>
        </div>

        <nav aria-label="主导航" className="shell-nav__list">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              className={({ isActive }) =>
                isActive ? "shell-link shell-link--active" : "shell-link"
              }
              end={item.end}
              to={item.to}
            >
              <span className="shell-link__label">{item.label}</span>
              <span className="shell-link__hint">{item.hint}</span>
            </NavLink>
          ))}
        </nav>

        <div className="shell-nav__footer">
          <span className="shell-chip shell-chip--success">基线已建立</span>
          <span className="shell-chip shell-chip--warning">Task 3 in progress</span>
        </div>
      </aside>

      <div className="shell-workspace">
        <header className="shell-context">
          <div>
            <p className="eyebrow">当前范围</p>
            <h2>单主 target 评测工作台</h2>
            <p className="body-muted">先切壳层与一级导航，再逐步补页面工作流。</p>
          </div>
          <div className="shell-context__meta">
            <span className="shell-chip">cockpit_agents</span>
            <span className="shell-chip">Evaluation Workbench</span>
            <NavLink className="shell-cta" to="/runs/new">
              开始运行
            </NavLink>
          </div>
        </header>

        <main className="shell-main" id="main-content">
          <Outlet />
        </main>
      </div>

      <aside aria-label="详情抽屉占位区" className="shell-sidepane">
        <div className="shell-sidepane__card">
          <p className="eyebrow">详情抽屉</p>
          <h3>侧边信息区</h3>
          <p className="body-muted">后续任务会在这里接入详情抽屉、操作反馈与风险提示。</p>
        </div>
      </aside>
    </div>
  );
}
