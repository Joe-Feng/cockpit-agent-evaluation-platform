import { describe, expect, test } from "vitest";

import { toneForSeverity, toneForStatus } from "../tone";

describe("toneForStatus", () => {
  test("maps known statuses into the shared cockpit tone system", () => {
    expect(toneForStatus("succeeded")).toBe("good");
    expect(toneForStatus("passed")).toBe("good");
    expect(toneForStatus("running")).toBe("warm");
    expect(toneForStatus("queued")).toBe("warm");
    expect(toneForStatus("failed")).toBe("danger");
    expect(toneForStatus("unknown")).toBe("neutral");
  });
});

describe("toneForSeverity", () => {
  test("maps severity labels into stable badge tones", () => {
    expect(toneForSeverity("high")).toBe("danger");
    expect(toneForSeverity("critical")).toBe("danger");
    expect(toneForSeverity("warning")).toBe("warm");
    expect(toneForSeverity("sev3")).toBe("warm");
    expect(toneForSeverity("info")).toBe("neutral");
    expect(toneForSeverity("low")).toBe("neutral");
  });
});
