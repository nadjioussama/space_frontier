/**
 * Tests for the Providers component — QueryClient setup and rendering.
 */
import React from "react";
import { render, screen } from "@testing-library/react";
import { useQueryClient } from "@tanstack/react-query";

// Mock OfflineBanner to avoid testing its internals here
jest.mock("@/components/OfflineBanner", () => ({
  OfflineBanner: () => <div data-testid="offline-banner" />,
}));

import { Providers } from "@/app/providers";

function InspectQueryClient() {
  const client = useQueryClient();
  const defaults = client.getDefaultOptions().queries;
  return (
    <div>
      <span data-testid="stale-time">{defaults?.staleTime}</span>
      <span data-testid="gc-time">{defaults?.gcTime}</span>
      <span data-testid="retry">{String(defaults?.retry)}</span>
      <span data-testid="refetch-focus">{String(defaults?.refetchOnWindowFocus)}</span>
    </div>
  );
}

describe("Providers", () => {
  it("renders children", () => {
    render(
      <Providers>
        <div data-testid="child">Hello</div>
      </Providers>
    );
    expect(screen.getByTestId("child")).toHaveTextContent("Hello");
  });

  it("includes OfflineBanner", () => {
    render(
      <Providers>
        <div />
      </Providers>
    );
    expect(screen.getByTestId("offline-banner")).toBeInTheDocument();
  });

  it("configures QueryClient with correct defaults", () => {
    render(
      <Providers>
        <InspectQueryClient />
      </Providers>
    );
    const HOUR = 60 * 60 * 1000;
    const DAY = 24 * HOUR;
    expect(screen.getByTestId("stale-time")).toHaveTextContent(String(HOUR));
    expect(screen.getByTestId("gc-time")).toHaveTextContent(String(DAY));
    expect(screen.getByTestId("retry")).toHaveTextContent("1");
    expect(screen.getByTestId("refetch-focus")).toHaveTextContent("false");
  });
});
