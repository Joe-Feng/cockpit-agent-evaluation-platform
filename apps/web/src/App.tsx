import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { WorkbenchPage } from "./pages/WorkbenchPage";
import { SuiteDetailPage } from "./pages/SuiteDetailPage";
import { SuiteLibraryPage } from "./pages/SuiteLibraryPage";

type PlaceholderPageProps = {
  eyebrow: string;
  title: string;
  description: string;
};

function PlaceholderPage({ eyebrow, title, description }: PlaceholderPageProps) {
  return (
    <section className="workbench-placeholder">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p className="body-muted">{description}</p>
    </section>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route
          path="/"
          element={<WorkbenchPage />}
        />
        <Route
          path="/suites"
          element={<SuiteLibraryPage />}
        />
        <Route
          path="/suites/:suiteId"
          element={<SuiteDetailPage />}
        />
        <Route
          path="/cases/new"
          element={
            <PlaceholderPage
              description="Case 新建页将在后续任务中接入结构化表单与版本化编辑流。"
              eyebrow="测试集"
              title="Create Case"
            />
          }
        />
        <Route
          path="/cases/:caseId/edit"
          element={
            <PlaceholderPage
              description="Case 编辑页将在后续任务中承接资产冻结与复制为新版本流程。"
              eyebrow="测试集"
              title="Edit Case"
            />
          }
        />
        <Route
          path="/imports/benchmark"
          element={
            <PlaceholderPage
              description="Benchmark 导入将在后续任务中补齐包预览、导入状态和来源摘要。"
              eyebrow="测试集"
              title="Benchmark Import"
            />
          }
        />
        <Route
          path="/runs"
          element={
            <PlaceholderPage
              description="运行模块将在后续任务中承接 run 列表、创建向导与详情视图。"
              eyebrow="运行"
              title="Run Workspace"
            />
          }
        />
        <Route
          path="/runs/new"
          element={
            <PlaceholderPage
              description="创建 Run 向导将在后续任务中接入 suite 选择、环境选择与提交反馈。"
              eyebrow="运行"
              title="Create Run"
            />
          }
        />
        <Route
          path="/runs/:runId"
          element={
            <PlaceholderPage
              description="Run 详情将在后续任务中承接任务明细、失败证据与报告摘要。"
              eyebrow="运行"
              title="Run Detail"
            />
          }
        />
        <Route
          path="/results"
          element={
            <PlaceholderPage
              description="结果模块将在后续任务中承接 case 历史、结果追溯与相关跳转。"
              eyebrow="结果"
              title="Case History"
            />
          }
        />
        <Route
          path="/risks"
          element={
            <PlaceholderPage
              description="风险中心将在后续任务中承接回归信号、告警与处理动作。"
              eyebrow="风险"
              title="Risk Center"
            />
          }
        />
        <Route
          path="/settings"
          element={
            <PlaceholderPage
              description="设置模块将在后续任务中承接默认 target、环境与工作台偏好配置。"
              eyebrow="设置"
              title="Workbench Settings"
            />
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
