import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { BenchmarkImportPage } from "./pages/BenchmarkImportPage";
import { CaseEditorPage } from "./pages/CaseEditorPage";
import { CaseHistoryPage } from "./pages/CaseHistoryPage";
import { RiskCenterPage } from "./pages/RiskCenterPage";
import { RunCreatePage } from "./pages/RunCreatePage";
import { RunDetailPage } from "./pages/RunDetailPage";
import { RunListPage } from "./pages/RunListPage";
import { SettingsPage } from "./pages/SettingsPage";
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
          element={<CaseHistoryPage />}
        />
        <Route
          path="/risks"
          element={<RiskCenterPage />}
        />
        <Route
          path="/settings"
          element={<SettingsPage />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
