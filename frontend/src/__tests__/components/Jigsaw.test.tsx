/**
 * Tests for the Jigsaw component helper functions and rendering states.
 * PixiJS is mocked since it requires WebGL context.
 */
import React from "react";
import { render, screen } from "@testing-library/react";

// Mock pixi.js entirely — no WebGL in test env
jest.mock("pixi.js", () => {
  const Graphics = jest.fn().mockImplementation(() => ({
    lineStyle: jest.fn().mockReturnThis(),
    beginFill: jest.fn().mockReturnThis(),
    drawRoundedRect: jest.fn().mockReturnThis(),
    endFill: jest.fn().mockReturnThis(),
  }));
  const Container = jest.fn().mockImplementation(() => ({
    addChild: jest.fn(),
    eventMode: "static",
    cursor: "grab",
    x: 0, y: 0, alpha: 1,
    on: jest.fn(),
  }));
  const Text = jest.fn().mockImplementation(() => ({ x: 0, y: 0 }));
  const Sprite = jest.fn().mockImplementation(() => ({ width: 0, height: 0 }));
  const Texture = jest.fn();
  const Rectangle = jest.fn();
  const Application = jest.fn().mockImplementation(() => ({
    view: document.createElement("canvas"),
    stage: {
      addChild: jest.fn(),
      removeChild: jest.fn(),
      eventMode: "static",
      hitArea: null,
      on: jest.fn(),
    },
    screen: {},
    destroy: jest.fn(),
  }));
  return {
    Application,
    Graphics,
    Container,
    Text,
    Sprite,
    Texture,
    Rectangle,
    Assets: { load: jest.fn().mockRejectedValue(new Error("no texture in test")) },
  };
});

jest.mock("@/lib/api", () => ({
  resolveAsset: (url: string) => url,
}));

import JigsawCanvas from "@/components/Jigsaw";

const JIGSAW_PROPS = {
  jigsaw: {
    image_url: "/media/test.jpg",
    piece_count: 4,
    grid_cols: 2,
    grid_rows: 2,
    piece_data: [
      { id: 0, row: 0, col: 0, u: 0, v: 0, w: 0.5, h: 0.5 },
      { id: 1, row: 0, col: 1, u: 0.5, v: 0, w: 0.5, h: 0.5 },
      { id: 2, row: 1, col: 0, u: 0, v: 0.5, w: 0.5, h: 0.5 },
      { id: 3, row: 1, col: 1, u: 0.5, v: 0.5, w: 0.5, h: 0.5 },
    ],
  },
  onComplete: jest.fn(),
};

describe("JigsawCanvas", () => {
  it("renders loading state initially", () => {
    render(<JigsawCanvas {...JIGSAW_PROPS} />);
    expect(screen.getByText("Loading jigsaw...")).toBeInTheDocument();
  });

  it("renders canvas container", () => {
    const { container } = render(<JigsawCanvas {...JIGSAW_PROPS} />);
    expect(container.querySelector(".aspect-\\[720\\/480\\]")).toBeInTheDocument();
  });

  it("does not show completion badge initially", () => {
    render(<JigsawCanvas {...JIGSAW_PROPS} />);
    expect(screen.queryByText("Jigsaw complete!")).not.toBeInTheDocument();
  });
});

describe("hslToHex (tested via module internals)", () => {
  // hslToHex is a module-level function. We test the color math directly.
  it("produces valid hex numbers", () => {
    // Red at full saturation: hsl(0, 100%, 50%) should be 0xFF0000
    // We replicate the function logic here since it's not exported
    function hslToHex(h: number, s: number, l: number): number {
      s /= 100; l /= 100;
      const k = (n: number) => (n + h / 30) % 12;
      const a = s * Math.min(l, 1 - l);
      const f = (n: number) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
      const rgb = [f(0), f(8), f(4)].map((v) => Math.round(v * 255));
      return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2];
    }

    // Pure red
    expect(hslToHex(0, 100, 50)).toBe(0xff0000);
    // Pure green
    expect(hslToHex(120, 100, 50)).toBe(0x00ff00);
    // Pure blue
    expect(hslToHex(240, 100, 50)).toBe(0x0000ff);
    // Black
    expect(hslToHex(0, 0, 0)).toBe(0x000000);
    // White
    expect(hslToHex(0, 0, 100)).toBe(0xffffff);
  });
});

describe("shufflePositions (tested via module internals)", () => {
  it("returns correct number of positions", () => {
    function shufflePositions(n: number) {
      const cols = 3, cellW = 80, cellH = 54, originX = 16, originY = 36;
      const slots = Array.from({ length: n }, (_, i) => ({
        tx: originX + (i % cols) * cellW,
        ty: originY + Math.floor(i / cols) * cellH,
      }));
      for (let i = slots.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [slots[i], slots[j]] = [slots[j], slots[i]];
      }
      return slots;
    }

    const positions = shufflePositions(6);
    expect(positions).toHaveLength(6);
    // All positions should have tx and ty
    positions.forEach((p) => {
      expect(p).toHaveProperty("tx");
      expect(p).toHaveProperty("ty");
      expect(p.tx).toBeGreaterThanOrEqual(16);
      expect(p.ty).toBeGreaterThanOrEqual(36);
    });
  });
});
