import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, test } from "vitest";

import App from "../../App";

describe("workbench app shell", () => {
  test("renders six primary modules and skip link", () => {
    render(
      <MemoryRouter
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
        initialEntries={["/"]}
      >
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByRole("link", { name: "跳到主内容" })).toBeTruthy();
    expect(screen.getByRole("navigation", { name: "主导航" })).toBeTruthy();
    expect(screen.getByRole("link", { name: /工作台/i })).toBeTruthy();
    expect(screen.getByRole("link", { name: /测试集/i })).toBeTruthy();
    expect(screen.getByRole("link", { name: /运行/i })).toBeTruthy();
    expect(screen.getByRole("link", { name: /结果/i })).toBeTruthy();
    expect(screen.getByRole("link", { name: /风险/i })).toBeTruthy();
    expect(screen.getByRole("link", { name: /设置/i })).toBeTruthy();
  });
});
