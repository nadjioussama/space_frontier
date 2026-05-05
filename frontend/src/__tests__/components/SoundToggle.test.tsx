import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SoundToggle } from "@/components/SoundToggle";
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

const mockToggleSound = jest.fn();
const mockUsePlayer = usePlayer as unknown as jest.Mock;

describe("SoundToggle", () => {
  it("renders unmute button when sound is muted", () => {
    mockUsePlayer.mockReturnValue({
      soundMuted: true,
      toggleSound: mockToggleSound,
    });

    render(<SoundToggle />);
    const button = screen.getByRole("button", { name: /unmute/i });
    expect(button).toBeInTheDocument();
  });

  it("renders mute button when sound is not muted", () => {
    mockUsePlayer.mockReturnValue({
      soundMuted: false,
      toggleSound: mockToggleSound,
    });

    render(<SoundToggle />);
    const button = screen.getByRole("button", { name: /mute/i });
    expect(button).toBeInTheDocument();
  });

  it("toggles sound state on click", async () => {
    const user = userEvent.setup();
    mockUsePlayer.mockReturnValue({
      soundMuted: false,
      toggleSound: mockToggleSound,
    });

    render(<SoundToggle />);
    const button = screen.getByRole("button");
    await user.click(button);

    expect(mockToggleSound).toHaveBeenCalledTimes(1);
  });

  it("displays correct icon based on muted state", () => {
    mockUsePlayer.mockReturnValue({
      soundMuted: false,
      toggleSound: mockToggleSound,
    });

    const { rerender } = render(<SoundToggle />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-label", "Mute sounds");

    mockUsePlayer.mockReturnValue({
      soundMuted: true,
      toggleSound: mockToggleSound,
    });

    rerender(<SoundToggle />);
    expect(screen.getByRole("button")).toHaveAttribute("aria-label", "Unmute sounds");
  });
});
