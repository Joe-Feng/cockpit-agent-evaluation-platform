import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { CaseExplorerPage } from "./pages/CaseExplorerPage";
import { RegressionCenterPage } from "./pages/RegressionCenterPage";
import { RunCenterPage } from "./pages/RunCenterPage";
import { TargetOverviewPage } from "./pages/TargetOverviewPage";
import { TrendDashboardPage } from "./pages/TrendDashboardPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<TargetOverviewPage />} />
        <Route path="/runs" element={<RunCenterPage />} />
        <Route path="/cases" element={<CaseExplorerPage />} />
        <Route path="/trends" element={<TrendDashboardPage />} />
        <Route path="/regressions" element={<RegressionCenterPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
