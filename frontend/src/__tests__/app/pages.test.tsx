/**
 * Tests for Next.js page components — integration-level rendering.
 */
import React from "react";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useParams: () => ({ slug: "test-mission" }),
  useRouter: () => ({ push: jest.fn(), back: jest.fn() }),
  usePathname: () => "/",
}));

// Mock next/link
jest.mock("next/link", () => {
  return ({ children, href, ...rest }: any) =>
    React.createElement("a", { href, ...rest }, children);
});

// Mock framer-motion
jest.mock("framer-motion", () => ({
  motion: {
    header: (props: any) => React.createElement("header", props),
    h1: (props: any) => React.createElement("h1", props),
    div: (props: any) => React.createElement("div", props),
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock all complex child components
jest.mock("@/components/SpaceMap", () => ({ SpaceMap: () => <div data-testid="space-map" /> }));
jest.mock("@/components/PlayerHud", () => ({ PlayerHud: () => <div data-testid="player-hud" /> }));
jest.mock("@/components/Leaderboard", () => ({ Leaderboard: () => <div data-testid="leaderboard" /> }));
jest.mock("@/components/Constellation", () => ({ ConstellationView: () => <div data-testid="constellation" /> }));
jest.mock("@/components/AgeGroupSelector", () => ({ AgeGroupSelector: () => <div data-testid="age-selector" /> }));
jest.mock("@/components/MissionViewport", () => ({ MissionViewport: ({ mission }: any) => <div data-testid="viewport">{mission.title}</div> }));
jest.mock("@/lib/sound", () => ({ SoundManager: { click: jest.fn() } }));
jest.mock("@/lib/api", () => ({ apiFetch: jest.fn() }));

// Mock queries hooks
jest.mock("@/lib/queries", () => ({
  useMission: jest.fn(),
}));

function createWrapper() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client }, children);
}

describe("HomePage", () => {
  it("renders all major sections", () => {
    // HomePage is a server component — we import and render directly
    const HomePage = require("@/app/page").default;
    render(<HomePage />);

    expect(screen.getByTestId("player-hud")).toBeInTheDocument();
    expect(screen.getByTestId("space-map")).toBeInTheDocument();
    expect(screen.getByTestId("leaderboard")).toBeInTheDocument();
    expect(screen.getByTestId("constellation")).toBeInTheDocument();
    expect(screen.getByTestId("age-selector")).toBeInTheDocument();
    expect(screen.getByText("NASA Space Explorer")).toBeInTheDocument();
  });

  it("renders footer with data sources", () => {
    const HomePage = require("@/app/page").default;
    render(<HomePage />);
    expect(screen.getByText(/Real NASA data from/)).toBeInTheDocument();
  });
});

describe("MissionPage", () => {
  it("renders loading state", () => {
    const { useMission } = require("@/lib/queries");
    useMission.mockReturnValue({ data: undefined, error: null, isLoading: true });

    const MissionPage = require("@/app/mission/[slug]/page").default;
    render(<MissionPage />, { wrapper: createWrapper() });

    expect(screen.getByText("Loading mission...")).toBeInTheDocument();
    expect(screen.getByTestId("player-hud")).toBeInTheDocument();
  });

  it("renders error state when no data", () => {
    const { useMission } = require("@/lib/queries");
    useMission.mockReturnValue({ data: undefined, error: new Error("fail"), isLoading: false });

    const MissionPage = require("@/app/mission/[slug]/page").default;
    render(<MissionPage />, { wrapper: createWrapper() });

    expect(screen.getByText(/couldn't load this mission/i)).toBeInTheDocument();
  });

  it("renders MissionViewport when data is available", () => {
    const { useMission } = require("@/lib/queries");
    const mission = { slug: "test", title: "Test Mission" };
    useMission.mockReturnValue({ data: mission, error: null, isLoading: false });

    const MissionPage = require("@/app/mission/[slug]/page").default;
    render(<MissionPage />, { wrapper: createWrapper() });

    expect(screen.getByTestId("viewport")).toHaveTextContent("Test Mission");
  });
});
