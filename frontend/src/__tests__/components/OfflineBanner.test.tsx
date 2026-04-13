import React from "react";
import { render, screen, act } from "@testing-library/react";
import { OfflineBanner } from "@/components/OfflineBanner";

describe("OfflineBanner", () => {
  let originalOnLine: PropertyDescriptor | undefined;

  beforeEach(() => {
    originalOnLine = Object.getOwnPropertyDescriptor(navigator, "onLine");
  });

  afterEach(() => {
    if (originalOnLine) {
      Object.defineProperty(navigator, "onLine", originalOnLine);
    } else {
      // Reset to default (true)
      Object.defineProperty(navigator, "onLine", {
        value: true,
        writable: true,
        configurable: true,
      });
    }
  });

  it("is hidden when online", () => {
    Object.defineProperty(navigator, "onLine", {
      value: true,
      writable: true,
      configurable: true,
    });

    const { container } = render(<OfflineBanner />);
    expect(container.innerHTML).toBe("");
  });

  it("shows banner when offline", () => {
    Object.defineProperty(navigator, "onLine", {
      value: false,
      writable: true,
      configurable: true,
    });

    render(<OfflineBanner />);
    expect(screen.getByText(/Offline/)).toBeInTheDocument();
  });

  it("contains offline message text", () => {
    Object.defineProperty(navigator, "onLine", {
      value: false,
      writable: true,
      configurable: true,
    });

    render(<OfflineBanner />);
    expect(
      screen.getByText(/playing from your saved missions/)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Progress syncs when you reconnect/)
    ).toBeInTheDocument();
  });

  it("responds to online/offline events", () => {
    Object.defineProperty(navigator, "onLine", {
      value: true,
      writable: true,
      configurable: true,
    });

    const { container } = render(<OfflineBanner />);
    expect(container.innerHTML).toBe("");

    // Simulate going offline
    act(() => {
      Object.defineProperty(navigator, "onLine", {
        value: false,
        writable: true,
        configurable: true,
      });
      window.dispatchEvent(new Event("offline"));
    });

    expect(screen.getByText(/Offline/)).toBeInTheDocument();

    // Simulate coming back online
    act(() => {
      Object.defineProperty(navigator, "onLine", {
        value: true,
        writable: true,
        configurable: true,
      });
      window.dispatchEvent(new Event("online"));
    });

    expect(container.querySelector("div")).toBeNull();
  });
});
