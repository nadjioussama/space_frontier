import React from "react";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import MissionsPage from "@/app/missions/page";
import { apiFetch } from "@/lib/api";

// Mock apiFetch
jest.mock("@/lib/api", () => ({
  apiFetch: jest.fn(),
}));

// Mock SoundManager
jest.mock("@/lib/sound", () => ({
  SoundManager: { click: jest.fn() },
}));

// Mock PlayerHud to simplify
jest.mock("@/components/PlayerHud", () => ({
  PlayerHud: () => <div data-testid="player-hud" />,
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("MissionsPage", () => {
  const mockPlanets = [
    { slug: "earth", name: "Earth" },
    { slug: "mars", name: "Mars" },
  ];

  const mockEarthDetail = {
    planet: { slug: "earth", name: "Earth" },
    missions: [
      { slug: "cross-1", title: "Cross Mission", mission_type: "cross_api", xp_reward: 100, difficulty: 5 },
      { slug: "apod-1", title: "APOD Mission", mission_type: "apod_daily", xp_reward: 50, difficulty: 2 },
    ],
  };

  beforeEach(() => {
    (apiFetch as jest.Mock).mockImplementation((url: string) => {
      if (url === "/api/v1/planets/") return Promise.resolve(mockPlanets);
      if (url === "/api/v1/planets/earth/") return Promise.resolve(mockEarthDetail);
      return Promise.resolve({});
    });
  });

  it("renders mission categories", async () => {
    render(<MissionsPage />, { wrapper: createWrapper() });

    expect(await screen.findByText("All Missions")).toBeInTheDocument();
    expect(await screen.findByText("Cross-API Missions")).toBeInTheDocument();
    expect(await screen.findByText("All Available Missions")).toBeInTheDocument();
  });

  it("renders specific missions from API data", async () => {
    render(<MissionsPage />, { wrapper: createWrapper() });

    expect(await screen.findByText("Cross Mission")).toBeInTheDocument();
    expect(await screen.findByText("APOD Mission")).toBeInTheDocument();
    expect(screen.getByText("Difficulty 5/10")).toBeInTheDocument();
    expect(screen.getByText("+100 XP")).toBeInTheDocument();
  });

  it("renders PlayerHud", () => {
    render(<MissionsPage />, { wrapper: createWrapper() });
    expect(screen.getByTestId("player-hud")).toBeInTheDocument();
  });
});
