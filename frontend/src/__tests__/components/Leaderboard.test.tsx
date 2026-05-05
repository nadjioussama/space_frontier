import React from "react";
import { render, screen } from "@testing-library/react";
import { Leaderboard } from "@/components/Leaderboard";
import { useWeeklyLeaderboard } from "@/lib/queries";


jest.mock("@/lib/queries", () => ({
  useWeeklyLeaderboard: jest.fn(),
}));

const mockUseWeeklyLeaderboard = useWeeklyLeaderboard as jest.Mock;

describe("Leaderboard", () => {
  it("shows loading state", () => {
    mockUseWeeklyLeaderboard.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });

    const { container } = render(<Leaderboard />);

    // Loading skeletons are rendered
    const skeletons = container.querySelectorAll(".skeleton");
    expect(skeletons.length).toBe(5);
  });

  it("renders leaderboard entries with rank, name, score", () => {
    mockUseWeeklyLeaderboard.mockReturnValue({
      data: {
        period: "weekly",
        entries: [
          { player_id: 1, display_name: "StarPilot", score: 5000, rank: 1 },
          { player_id: 2, display_name: "MoonWalker", score: 3200, rank: 2 },
          { player_id: 3, display_name: "CosmicRay", score: 1800, rank: 3 },
        ],
      },
      isLoading: false,
      error: null,
    });

    render(<Leaderboard />);

    expect(screen.getByText("#1")).toBeInTheDocument();
    expect(screen.getByText("StarPilot")).toBeInTheDocument();
    expect(screen.getByText("5,000 XP")).toBeInTheDocument();

    expect(screen.getByText("#2")).toBeInTheDocument();
    expect(screen.getByText("MoonWalker")).toBeInTheDocument();
    expect(screen.getByText("3,200 XP")).toBeInTheDocument();

    expect(screen.getByText("#3")).toBeInTheDocument();
    expect(screen.getByText("CosmicRay")).toBeInTheDocument();
    expect(screen.getByText("1,800 XP")).toBeInTheDocument();
  });

  it("shows empty state", () => {
    mockUseWeeklyLeaderboard.mockReturnValue({
      data: { period: "weekly", entries: [] },
      isLoading: false,
      error: null,
    });

    render(<Leaderboard />);

    expect(screen.getByText(/No scores yet this week/)).toBeInTheDocument();
  });

  it("shows error state", () => {
    mockUseWeeklyLeaderboard.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("Network error"),
    });

    render(<Leaderboard />);

    expect(screen.getByText(/Leaderboard unavailable/)).toBeInTheDocument();
  });

  it("shows the weekly leaderboard heading", () => {
    mockUseWeeklyLeaderboard.mockReturnValue({
      data: { period: "weekly", entries: [] },
      isLoading: false,
      error: null,
    });

    render(<Leaderboard />);

    expect(screen.getByText("Weekly Leaderboard")).toBeInTheDocument();
  });
});
