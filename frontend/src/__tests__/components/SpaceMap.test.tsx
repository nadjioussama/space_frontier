import React from "react";
import { render, screen } from "@testing-library/react";
import { SpaceMap } from "@/components/SpaceMap";
import { useToday, usePlanets } from "@/lib/queries";


jest.mock("@/lib/sound", () => ({
  SoundManager: {
    click: jest.fn(),
    transition: jest.fn(),
    init: jest.fn(),
  },
}));

jest.mock("@/lib/queries", () => ({
  useToday: jest.fn(),
  usePlanets: jest.fn(),
}));

const mockUseToday = useToday as jest.Mock;
const mockUsePlanets = usePlanets as jest.Mock;

describe("SpaceMap", () => {
  beforeEach(() => {
    mockUseToday.mockReturnValue({
      data: {
        apod: { date: "2025-01-01", title: "Test", explanation: "Test", media_type: "image", image: "/test.jpg" },
        mission_slug: "earth-mission-1",
        neo_approaching_count: 3,
      },
    });
    mockUsePlanets.mockReturnValue({
      data: [
        { slug: "earth", name: "Earth", description: "", is_unlocked: true, mission_count: 5 },
        { slug: "mars", name: "Mars", description: "", is_unlocked: true, mission_count: 3 },
        { slug: "asteroid-belt", name: "Asteroids", description: "", is_unlocked: false, mission_count: 0 },
      ],
    });
  });

  it("renders planet nodes", () => {
    render(<SpaceMap />);

    expect(screen.getByText("Earth")).toBeInTheDocument();
    expect(screen.getByText("Mars")).toBeInTheDocument();
    expect(screen.getByText("Asteroids")).toBeInTheDocument();
  });

  it("locked planets are not clickable links", () => {
    render(<SpaceMap />);

    // Asteroids is locked, so it should not be a link
    const asteroids = screen.getByText("Asteroids");
    const link = asteroids.closest("a");
    expect(link).toBeNull();

    // It should show "locked" text
    expect(screen.getByText("locked")).toBeInTheDocument();
  });

  it("unlocked planets link to /mission/{slug}", () => {
    render(<SpaceMap />);

    // Earth is unlocked and should link to /mission/earth-mission-1 (today's slug)
    const earthLink = screen.getByText("Earth").closest("a");
    expect(earthLink).toHaveAttribute("href", "/mission/earth-mission-1");

    // Mars is unlocked and should link to /mission/mars
    const marsLink = screen.getByText("Mars").closest("a");
    expect(marsLink).toHaveAttribute("href", "/mission/mars");
  });

  it("shows fallback when no data", () => {
    mockUsePlanets.mockReturnValue({ data: undefined });

    render(<SpaceMap />);

    // Should show fallback nodes
    expect(screen.getByText("Earth")).toBeInTheDocument();
    expect(screen.getByText("Mars")).toBeInTheDocument();
    expect(screen.getByText("Asteroids")).toBeInTheDocument();
    expect(screen.getByText("Exoplanets")).toBeInTheDocument();
  });

  it('displays "Explore the cosmos" subtitle when no NEO count', () => {
    mockUseToday.mockReturnValue({
      data: {
        apod: { date: "2025-01-01", title: "Test", explanation: "Test", media_type: "image", image: "/test.jpg" },
        mission_slug: "earth-mission-1",
      },
    });

    render(<SpaceMap />);

    expect(screen.getByText("Explore the cosmos")).toBeInTheDocument();
  });

  it("displays NEO approaching count when available", () => {
    render(<SpaceMap />);

    expect(screen.getByText("3 NEOs approaching today")).toBeInTheDocument();
  });

  it("shows Cross-API Missions link", () => {
    render(<SpaceMap />);

    const crossApiLink = screen.getByText(/Cross-API Missions/);
    expect(crossApiLink.closest("a")).toHaveAttribute("href", "/missions");
  });
});
