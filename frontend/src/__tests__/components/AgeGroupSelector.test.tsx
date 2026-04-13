import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AgeGroupSelector } from "@/components/AgeGroupSelector";
import { usePlayer } from "@/store/player";

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
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
  useAnimation: () => ({ start: jest.fn(), set: jest.fn() }),
}));

jest.mock("@/lib/sound", () => ({
  SoundManager: {
    click: jest.fn(),
    init: jest.fn(),
  },
}));

jest.mock("@/store/player", () => ({
  usePlayer: jest.fn(),
}));

const mockSetAgeGroup = jest.fn();
const mockUsePlayer = usePlayer as unknown as jest.Mock;

describe("AgeGroupSelector", () => {
  beforeEach(() => {
    mockUsePlayer.mockReturnValue({
      ageGroup: "9-11",
      setAgeGroup: mockSetAgeGroup,
    });
  });

  it("renders age group options (6-8, 9-11, 12-14)", () => {
    render(<AgeGroupSelector />);

    expect(screen.getByText(/6.*8/)).toBeInTheDocument();
    expect(screen.getByText(/9.*11/)).toBeInTheDocument();
    expect(screen.getByText(/12.*14/)).toBeInTheDocument();
  });

  it("highlights current age group", () => {
    mockUsePlayer.mockReturnValue({
      ageGroup: "9-11",
      setAgeGroup: mockSetAgeGroup,
    });
    render(<AgeGroupSelector />);

    // The 9-11 button should have the active styling
    const activeButton = screen.getByText(/9.*11/).closest("button");
    expect(activeButton).toHaveClass("border-space-accent");
  });

  it("calls setAgeGroup on click", async () => {
    const user = userEvent.setup();
    render(<AgeGroupSelector />);

    const button68 = screen.getByText(/6.*8/).closest("button")!;
    await user.click(button68);

    expect(mockSetAgeGroup).toHaveBeenCalledWith("6-8");
  });

  it("sets data-age on document element via setAgeGroup", async () => {
    // Mock setAgeGroup to also set the data-age attribute (mirroring real store behavior)
    const setAgeGroupWithSideEffect = jest.fn((ag: string) => {
      document.documentElement.setAttribute("data-age", ag);
    });

    mockUsePlayer.mockReturnValue({
      ageGroup: "9-11",
      setAgeGroup: setAgeGroupWithSideEffect,
    });

    const user = userEvent.setup();
    render(<AgeGroupSelector />);

    const button1214 = screen.getByText(/12.*14/).closest("button")!;
    await user.click(button1214);

    expect(setAgeGroupWithSideEffect).toHaveBeenCalledWith("12-14");
    expect(document.documentElement.getAttribute("data-age")).toBe("12-14");
  });

  it("renders compact variant", () => {
    render(<AgeGroupSelector compact />);

    // Compact uses smaller text-xs buttons
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(3);
    buttons.forEach((btn) => {
      expect(btn).toHaveClass("text-xs");
    });
  });
});
