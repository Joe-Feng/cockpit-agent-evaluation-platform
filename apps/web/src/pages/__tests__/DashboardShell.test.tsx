import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, vi } from "vitest";

import App from "../../App";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: true,
      json: async () => ({
        target_id: "cockpit_agents",
        latest_status: "unknown",
        latest_runs: [],
        open_alerts: [],
      }),
    })),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

test("renders all phase 3 navigation entries", async () => {
  render(
    <MemoryRouter
      future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      initialEntries={["/"]}
    >
      <App />
    </MemoryRouter>,
  );

  await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());
  expect(screen.getAllByText("Target Overview").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Run Center").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Case Explorer").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Trend Dashboard").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Regression Center").length).toBeGreaterThan(0);
});
