"use client";
// PixiJS jigsaw, Phase 1+2 quality: grid-based pieces, drag-and-snap.
// Irregular edges, animated assembly, particle reward = Phase 6.
//
// This component is imported dynamically (ssr:false) so Pixi's DOM/GL calls
// never run during Next.js server rendering.
import { useEffect, useRef, useState } from "react";
import { resolveAsset } from "@/lib/api";
import type { Jigsaw } from "@/lib/api";

type Props = {
  jigsaw: Jigsaw;
  onComplete: () => void;
};

const STAGE_W = 720;
const STAGE_H = 480;
const SNAP_TOLERANCE_PX = 22;

export default function JigsawCanvas({ jigsaw, onComplete }: Props) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [ready, setReady] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let destroyed = false;
    let app: any = null;

    (async () => {
      try {
        const PIXI = await import("pixi.js");
        if (destroyed || !hostRef.current) return;

        app = new PIXI.Application({
          width: STAGE_W,
          height: STAGE_H,
          backgroundAlpha: 0,
          antialias: true,
        });
        hostRef.current.innerHTML = "";
        hostRef.current.appendChild(app.view as unknown as HTMLCanvasElement);

        // Size the board region to fit the image's aspect ratio inside the stage.
        // We display the target at half the stage height to leave room for pieces.
        const boardW = STAGE_W * 0.55;
        const boardH = STAGE_H * 0.9;
        const boardX = (STAGE_W - boardW) - 8;
        const boardY = (STAGE_H - boardH) / 2;

        // Board placeholder + outline
        const boardBg = new PIXI.Graphics();
        boardBg.lineStyle({ width: 2, color: 0x66d9ff, alpha: 0.35 });
        boardBg.beginFill(0x0b1023, 0.6);
        boardBg.drawRoundedRect(boardX, boardY, boardW, boardH, 12);
        boardBg.endFill();
        app.stage.addChild(boardBg);

        // Load the source image as a texture. If loading fails (e.g. CORS or
        // hotlink block), we fall back to a plain fill so the UX doesn't deadend.
        let sourceTex: any = null;
        try {
          sourceTex = await PIXI.Assets.load(resolveAsset(jigsaw.image_url));
        } catch {
          // Continue with null -> pieces render as colored tiles.
        }

        const pieceBaseW = boardW / jigsaw.grid_cols;
        const pieceBaseH = boardH / jigsaw.grid_rows;

        const pieces: any[] = [];
        const placed = new Set<number>();

        const tray = shufflePositions(jigsaw.piece_data.length);

        for (const def of jigsaw.piece_data) {
          const piece = new PIXI.Container();
          piece.eventMode = "static";
          piece.cursor = "grab";

          // Build the sprite using a region of the source texture; fall back
          // to a solid color keyed on piece id if we couldn't load the image.
          if (sourceTex?.baseTexture) {
            const frame = new PIXI.Rectangle(
              def.u * sourceTex.width,
              def.v * sourceTex.height,
              def.w * sourceTex.width,
              def.h * sourceTex.height
            );
            const pieceTex = new PIXI.Texture(sourceTex.baseTexture, frame);
            const sprite = new PIXI.Sprite(pieceTex);
            sprite.width = pieceBaseW;
            sprite.height = pieceBaseH;
            piece.addChild(sprite);
          } else {
            const g = new PIXI.Graphics();
            const hue = (def.id * 47) % 360;
            g.beginFill(hslToHex(hue, 70, 55));
            g.drawRoundedRect(0, 0, pieceBaseW, pieceBaseH, 4);
            g.endFill();
            piece.addChild(g);
          }

          // Thin border so adjacent pieces are visible on the board.
          const border = new PIXI.Graphics();
          border.lineStyle({ width: 1, color: 0xffffff, alpha: 0.18 });
          border.drawRoundedRect(0, 0, pieceBaseW, pieceBaseH, 4);
          piece.addChild(border);

          // Initial scattered position in the left tray area.
          const slot = tray.pop() ?? { tx: 20, ty: 20 };
          piece.x = slot.tx;
          piece.y = slot.ty;

          // The correct landing coordinates on the board.
          (piece as any).__targetX = boardX + def.col * pieceBaseW;
          (piece as any).__targetY = boardY + def.row * pieceBaseH;
          (piece as any).__id = def.id;

          attachDrag(PIXI, app, piece, (p) => {
            const targetX = (p as any).__targetX;
            const targetY = (p as any).__targetY;
            const dx = Math.abs(p.x - targetX);
            const dy = Math.abs(p.y - targetY);
            if (dx < SNAP_TOLERANCE_PX && dy < SNAP_TOLERANCE_PX) {
              p.x = targetX;
              p.y = targetY;
              p.eventMode = "none";
              p.cursor = "default";
              p.alpha = 0.95;
              placed.add((p as any).__id);
              if (placed.size === jigsaw.piece_data.length && !completed) {
                setCompleted(true);
                onComplete();
              }
            }
          });

          app.stage.addChild(piece);
          pieces.push(piece);
        }

        // Label bands
        const instr = new PIXI.Text(
          "Drag pieces into the outlined board.",
          { fill: 0xffffff, fontSize: 14, fontFamily: "Nunito" }
        );
        instr.x = 12;
        instr.y = 10;
        app.stage.addChild(instr);

        setReady(true);
      } catch (e: any) {
        setError(e?.message ?? "Failed to load the puzzle.");
      }
    })();

    return () => {
      destroyed = true;
      try {
        app?.destroy(true, { children: true, texture: false, baseTexture: false });
      } catch {
        /* ignore */
      }
    };
    // We deliberately run once per mission — jigsaw changes with the mission prop
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jigsaw.image_url, jigsaw.piece_count]);

  return (
    <div className="relative w-full">
      <div
        ref={hostRef}
        className="w-full aspect-[720/480] bg-black/40 rounded-xl border border-white/10 overflow-hidden"
      />
      {!ready && !error && (
        <div className="absolute inset-0 grid place-items-center text-white/60 text-sm">
          Loading jigsaw...
        </div>
      )}
      {error && (
        <div className="absolute inset-0 grid place-items-center text-space-warn text-sm p-4 text-center">
          Puzzle could not load: {error}
        </div>
      )}
      {completed && (
        <div className="absolute top-2 right-2 bg-space-ok/20 text-space-ok border border-space-ok/50 rounded px-2 py-1 text-xs font-display">
          Jigsaw complete!
        </div>
      )}
    </div>
  );
}

// --- helpers -----------------------------------------------------------

function attachDrag(PIXI: any, app: any, target: any, onDrop: (t: any) => void) {
  let dragging = false;
  let offset = { x: 0, y: 0 };

  const onDown = (e: any) => {
    dragging = true;
    target.alpha = 0.8;
    target.cursor = "grabbing";
    const pos = e.getLocalPosition(app.stage);
    offset = { x: pos.x - target.x, y: pos.y - target.y };
    // Bring to front
    app.stage.removeChild(target);
    app.stage.addChild(target);
  };
  const onUp = () => {
    if (!dragging) return;
    dragging = false;
    target.alpha = 1;
    target.cursor = "grab";
    onDrop(target);
  };
  const onMove = (e: any) => {
    if (!dragging) return;
    const pos = e.getLocalPosition(app.stage);
    target.x = pos.x - offset.x;
    target.y = pos.y - offset.y;
  };

  target.on("pointerdown", onDown);
  // Listen on the stage so fast drags don't lose the pointer.
  app.stage.eventMode = "static";
  app.stage.hitArea = app.screen;
  app.stage.on("pointerup", onUp);
  app.stage.on("pointerupoutside", onUp);
  app.stage.on("pointermove", onMove);
}

function shufflePositions(n: number): Array<{ tx: number; ty: number }> {
  // Lay tiles out in a left-side tray, shuffled.
  const cols = 3;
  const cellW = 80;
  const cellH = 54;
  const originX = 16;
  const originY = 36;
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

function hslToHex(h: number, s: number, l: number): number {
  s /= 100; l /= 100;
  const k = (n: number) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n: number) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  const rgb = [f(0), f(8), f(4)].map((v) => Math.round(v * 255));
  return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2];
}
