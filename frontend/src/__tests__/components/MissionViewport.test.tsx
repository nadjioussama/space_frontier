import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MissionViewport } from "@/components/MissionViewport";
import { usePlayer } from "@/store/player";
import type { MissionDetail } from "@/lib/api";

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
    header: ({ children, ...props }: any) => <header {...props}>{children}</header>,
    h1: ({ children, ...props }: any) => <h1 {...props}>{children}</h1>,
    section: ({ children, ...props }: any) => <section {...props}>{children}</section>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
  useAnimation: () => ({ start: jest.fn(), set: jest.fn() }),
}));

jest.mock("@/lib/sound", () => ({
  SoundManager: {
    click: jest.fn(),
    transition: jest.fn(),
    correct: jest.fn(),
    wrong: jest.fn(),
    achievement: jest.fn(),
    collect: jest.fn(),
    init: jest.fn(),
  },
}));

jest.mock("@/store/player", () => ({
  usePlayer: jest.fn(),
}));

const mockAddXp = jest.fn();
const mockMarkCompleted = jest.fn();
const mockSetDDALevel = jest.fn();
const mockIncrementStreak = jest.fn();
const mockUsePlayer = usePlayer as unknown as jest.Mock;

const MOCK_MISSION: MissionDetail = {
  slug: "test-mission",
  title: "Explore the Solar System",
  mission_type: "apod",
  xp_reward: 100,
  difficulty: 5,
  apod: {
    date: "2025-01-15",
    title: "A Stunning Nebula",
    explanation: "This beautiful nebula was captured by the Hubble telescope.",
    media_type: "image",
    image: "/test-image.jpg",
    copyright: "NASA/ESA",
  },
  jigsaw: null,
  quizzes: [
    {
      id: 1,
      question: "What is the closest star to Earth?",
      options: ["The Sun", "Alpha Centauri", "Proxima Centauri", "Sirius"],
      difficulty: 3,
    },
    {
      id: 2,
      question: "How many planets are in the solar system?",
      options: ["7", "8", "9", "10"],
      difficulty: 2,
    },
  ],
};

describe("MissionViewport", () => {
  beforeEach(() => {
    mockUsePlayer.mockImplementation((selector?: any) => {
      const state = {
        addXp: mockAddXp,
        markCompleted: mockMarkCompleted,
        setDDALevel: mockSetDDALevel,
        incrementStreak: mockIncrementStreak,
      };
      if (typeof selector === "function") {
        return selector(state);
      }
      return state;
    });

    // Mock global fetch
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("renders mission title", () => {
    render(<MissionViewport mission={MOCK_MISSION} />);

    expect(screen.getByText("Explore the Solar System")).toBeInTheDocument();
  });

  it("renders XP reward", () => {
    render(<MissionViewport mission={MOCK_MISSION} />);

    expect(screen.getByText("+100 XP")).toBeInTheDocument();
  });

  it("renders difficulty", () => {
    render(<MissionViewport mission={MOCK_MISSION} />);

    expect(screen.getByText("Difficulty 5/10")).toBeInTheDocument();
  });

  it("shows APOD content when present", () => {
    render(<MissionViewport mission={MOCK_MISSION} />);

    expect(screen.getByText(/NASA Picture of the Day/)).toBeInTheDocument();
    expect(screen.getByText(/2025-01-15/)).toBeInTheDocument();
    expect(
      screen.getByText(/This beautiful nebula was captured/)
    ).toBeInTheDocument();
    expect(screen.getByText(/NASA\/ESA/)).toBeInTheDocument();
  });

  it("does not show APOD section when apod is null", () => {
    const missionNoApod = { ...MOCK_MISSION, apod: null };
    render(<MissionViewport mission={missionNoApod} />);

    expect(screen.queryByText(/NASA Picture of the Day/)).not.toBeInTheDocument();
  });

  it("displays quiz panel", () => {
    render(<MissionViewport mission={MOCK_MISSION} />);

    expect(screen.getByText("Quiz")).toBeInTheDocument();
    expect(screen.getByText("What is the closest star to Earth?")).toBeInTheDocument();
    expect(screen.getByText("How many planets are in the solar system?")).toBeInTheDocument();
    expect(screen.getByText("Submit Answers")).toBeInTheDocument();
  });

  it("handles submission and shows results", async () => {
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        xp_earned: 80,
        results: [{ correct: true }, { correct: false }],
        progress: { dda: { level: 4, accuracy: 0.65 } },
      }),
    });

    render(<MissionViewport mission={MOCK_MISSION} />);

    // Answer both questions
    await user.click(screen.getByText("The Sun"));
    await user.click(screen.getByText("8"));

    // Submit
    await user.click(screen.getByText("Submit Answers"));

    // Wait for results to appear
    await waitFor(() => {
      expect(screen.getByText(/Mission complete/)).toBeInTheDocument();
    });

    expect(screen.getByText(/\+80 XP/)).toBeInTheDocument();
    expect(screen.getByText(/1 of 2/)).toBeInTheDocument();

    // Verify player state updates
    expect(mockAddXp).toHaveBeenCalledWith(80);
    expect(mockMarkCompleted).toHaveBeenCalledWith("test-mission");
    expect(mockIncrementStreak).toHaveBeenCalled();
    expect(mockSetDDALevel).toHaveBeenCalledWith(4);
  });

  it("handles offline submission gracefully", async () => {
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("Network error"));

    render(<MissionViewport mission={MOCK_MISSION} />);

    // Answer both questions
    await user.click(screen.getByText("The Sun"));
    await user.click(screen.getByText("8"));

    // Submit
    await user.click(screen.getByText("Submit Answers"));

    // Wait for offline results
    await waitFor(() => {
      expect(screen.getByText(/Mission complete/)).toBeInTheDocument();
    });

    // Offline gives 50% XP
    expect(mockAddXp).toHaveBeenCalledWith(50);
    expect(screen.getByText(/Submitted offline/)).toBeInTheDocument();
  });

  it("shows Cross-API badge for cross-api missions", () => {
    const crossApiMission = { ...MOCK_MISSION, is_cross_api: true };
    render(<MissionViewport mission={crossApiMission} />);

    expect(screen.getByText("Cross-API")).toBeInTheDocument();
  });

  it("shows return to Space Map link after completion", async () => {
    const user = userEvent.setup();

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        xp_earned: 100,
        results: [{ correct: true }, { correct: true }],
        progress: { dda: { level: 3, accuracy: 0.8 } },
      }),
    });

    render(<MissionViewport mission={MOCK_MISSION} />);

    await user.click(screen.getByText("The Sun"));
    await user.click(screen.getByText("8"));
    await user.click(screen.getByText("Submit Answers"));

    await waitFor(() => {
      expect(screen.getByText(/Return to Space Map/)).toBeInTheDocument();
    });

    const returnLink = screen.getByText(/Return to Space Map/).closest("a");
    expect(returnLink).toHaveAttribute("href", "/");
  });
});
