import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { BenchmarkImportPage } from "./pages/BenchmarkImportPage";
import { CaseEditorPage } from "./pages/CaseEditorPage";
import { RunCreatePage } from "./pages/RunCreatePage";
import { RunDetailPage } from "./pages/RunDetailPage";
import { RunListPage } from "./pages/RunListPage";
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
          element={<CaseEditorPage />}
        />
        <Route
          path="/cases/:caseId/edit"
          element={<CaseEditorPage />}
        />
        <Route
          path="/imports/benchmark"
          element={<BenchmarkImportPage />}
        />
        <Route
          path="/runs"
          element={<RunListPage />}
        />
        <Route
          path="/runs/new"
          element={<RunCreatePage />}
        />
        <Route
          path="/runs/:runId"
          element={<RunDetailPage />}
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
