import React from "react";
import { render, screen } from "@testing-library/react";
import { PlayerHud } from "@/components/PlayerHud";
import { usePlayer } from "@/store/player";


jest.mock("@/lib/sound", () => ({
  SoundManager: {
    init: jest.fn(),
    updateSettings: jest.fn(),
    toggleMute: jest.fn(),
    click: jest.fn(),
  },
}));

jest.mock("@/store/player", () => ({
  usePlayer: jest.fn(),
}));

const mockRehydrate = jest.fn();
const mockToggleSound = jest.fn();
const mockUsePlayer = usePlayer as unknown as jest.Mock;

describe("PlayerHud", () => {
  beforeEach(() => {
    // Default mock: usePlayer is called both as a hook (no args) and with a selector
    // PlayerHud calls usePlayer() without a selector, getting the full state
    mockUsePlayer.mockReturnValue({
      rank: "Captain",
      totalXp: 1250,
      streak: 5,
      ddaLevel: 4,
      soundMuted: false,
      toggleSound: mockToggleSound,
      _rehydrate: mockRehydrate,
    });
  });

  it("displays rank", () => {
    render(<PlayerHud />);
    expect(screen.getByText("Captain")).toBeInTheDocument();
  });

  it("displays XP", () => {
    render(<PlayerHud />);
    expect(screen.getByText("1,250")).toBeInTheDocument();
    expect(screen.getByText(/XP/)).toBeInTheDocument();
  });

  it("displays streak when greater than 0", () => {
    render(<PlayerHud />);
    expect(screen.getByText(/5d/)).toBeInTheDocument();
  });

  it("displays DDA level", () => {
    render(<PlayerHud />);
    expect(screen.getByText("Lv.4")).toBeInTheDocument();
  });

  it("contains SoundToggle", () => {
    render(<PlayerHud />);
    // SoundToggle renders a button with aria-label "Mute sounds"
    const soundButton = screen.getByRole("button", { name: /mute/i });
    expect(soundButton).toBeInTheDocument();
  });

  it("calls _rehydrate on mount", () => {
    render(<PlayerHud />);
    expect(mockRehydrate).toHaveBeenCalled();
  });

  it("does not show streak when streak is 0", () => {
    mockUsePlayer.mockReturnValue({
      rank: "Cadet",
      totalXp: 50,
      streak: 0,
      ddaLevel: 3,
      soundMuted: false,
      toggleSound: mockToggleSound,
      _rehydrate: mockRehydrate,
    });

    render(<PlayerHud />);
    expect(screen.queryByText(/0d/)).not.toBeInTheDocument();
  });
});
