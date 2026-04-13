import React from "react";
import { render, screen } from "@testing-library/react";
import { ConstellationView } from "@/components/Constellation";
import { useConstellations } from "@/lib/queries";
import type { ConstellationData } from "@/lib/api";

jest.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
    a: ({ children, ...props }: any) => <a {...props}>{children}</a>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    li: ({ children, ...props }: any) => <li {...props}>{children}</li>,
    svg: ({ children, ...props }: any) => <svg {...props}>{children}</svg>,
    circle: ({ children, ...props }: any) => <circle {...props}>{children}</circle>,
    path: (props: any) => <path {...props} />,
    line: (props: any) => <line {...props} />,
    g: ({ children, ...props }: any) => <g {...props}>{children}</g>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
  useAnimation: () => ({ start: jest.fn(), set: jest.fn() }),
}));

jest.mock("@/lib/queries", () => ({
  useConstellations: jest.fn(),
}));

const mockUseConstellations = useConstellations as jest.Mock;

const MOCK_CONSTELLATIONS: ConstellationData[] = [
  {
    slug: "solar-system",
    name: "Solar System",
    topic: "planets",
    description: "Learn about planets",
    icon: "planet",
    earned_count: 2,
    total_count: 5,
    stars: [
      {
        id: 1,
        slug: "mercury",
        name: "Mercury",
        description: "Closest to Sun",
        xp_value: 100,
        x: 20,
        y: 30,
        earned: true,
        prerequisites: [],
      },
      {
        id: 2,
        slug: "venus",
        name: "Venus",
        description: "Second planet",
        xp_value: 100,
        x: 40,
        y: 50,
        earned: true,
        prerequisites: ["mercury"],
      },
      {
        id: 3,
        slug: "earth-star",
        name: "Earth",
        description: "Our home",
        xp_value: 100,
        x: 60,
        y: 40,
        earned: false,
        prerequisites: ["venus"],
      },
    ],
  },
  {
    slug: "deep-space",
    name: "Deep Space",
    topic: "galaxies",
    description: "Explore galaxies",
    icon: "galaxy",
    earned_count: 0,
    total_count: 3,
    stars: [
      {
        id: 4,
        slug: "milky-way",
        name: "Milky Way",
        description: "Our galaxy",
        xp_value: 200,
        x: 50,
        y: 50,
        earned: false,
        prerequisites: [],
      },
    ],
  },
];

describe("ConstellationView", () => {
  it("shows loading state", () => {
    mockUseConstellations.mockReturnValue({
      data: undefined,
      isLoading: true,
    });

    const { container } = render(<ConstellationView />);

    const skeletons = container.querySelectorAll(".skeleton");
    expect(skeletons.length).toBe(3);
  });

  it("renders constellation names", () => {
    mockUseConstellations.mockReturnValue({
      data: MOCK_CONSTELLATIONS,
      isLoading: false,
    });

    render(<ConstellationView />);

    expect(screen.getByText("Solar System")).toBeInTheDocument();
    expect(screen.getByText("Deep Space")).toBeInTheDocument();
  });

  it("renders stars with earned/unearned states", () => {
    mockUseConstellations.mockReturnValue({
      data: MOCK_CONSTELLATIONS,
      isLoading: false,
    });

    const { container } = render(<ConstellationView />);

    // Check for star text labels rendered in SVG
    expect(screen.getByText("Mercury")).toBeInTheDocument();
    expect(screen.getByText("Venus")).toBeInTheDocument();
    expect(screen.getByText("Earth")).toBeInTheDocument();

    // Earned stars (Mercury, Venus) have fill="#F0A500" and r=6
    // Unearned stars (Earth) have fill="#1B2735" and r=4
    const circles = container.querySelectorAll("circle");
    const earnedCircles = Array.from(circles).filter(
      (c) => c.getAttribute("fill") === "#F0A500" && c.getAttribute("r") === "6"
    );
    const unearnedCircles = Array.from(circles).filter(
      (c) => c.getAttribute("fill") === "#1B2735" && c.getAttribute("r") === "4"
    );

    // 2 earned stars (Mercury, Venus) + each has a glow circle
    expect(earnedCircles.length).toBe(2);
    // 2 unearned stars (Earth in solar system, Milky Way in deep space)
    expect(unearnedCircles.length).toBe(2);
  });

  it("shows placeholder when empty", () => {
    mockUseConstellations.mockReturnValue({
      data: [],
      isLoading: false,
    });

    render(<ConstellationView />);

    expect(screen.getByText("Knowledge Constellation")).toBeInTheDocument();
    expect(
      screen.getByText(/Complete missions to discover your first stars/)
    ).toBeInTheDocument();
  });

  it("shows earned_count / total_count", () => {
    mockUseConstellations.mockReturnValue({
      data: MOCK_CONSTELLATIONS,
      isLoading: false,
    });

    render(<ConstellationView />);

    expect(screen.getByText("2/5")).toBeInTheDocument();
    expect(screen.getByText("0/3")).toBeInTheDocument();
  });

  it("shows 'Your Night Sky' heading when data exists", () => {
    mockUseConstellations.mockReturnValue({
      data: MOCK_CONSTELLATIONS,
      isLoading: false,
    });

    render(<ConstellationView />);

    expect(screen.getByText("Your Night Sky")).toBeInTheDocument();
  });
});
