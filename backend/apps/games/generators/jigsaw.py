"""Minimal jigsaw generator. PLAN §7.5.

For the walking skeleton we describe the puzzle with a regular grid —
frontend shuffles the pieces and renders the correct sub-rects of the image.
Irregular interlocking edges, piece PNGs to S3, etc. are Phase 6 polish.
"""
from __future__ import annotations

from ..models import JigsawPuzzle, Mission


def _grid_for(piece_count: int) -> tuple[int, int]:
    return {12: (4, 3), 24: (6, 4), 48: (8, 6)}.get(piece_count, (4, 3))


def build_grid_pieces(cols: int, rows: int) -> list[dict]:
    pieces: list[dict] = []
    w = 1 / cols
    h = 1 / rows
    for r in range(rows):
        for c in range(cols):
            pieces.append({
                "id": r * cols + c,
                "row": r,
                "col": c,
                # Fractional coordinates of the piece inside the source image.
                # Renderer multiplies by actual image dimensions.
                "u": round(c * w, 6),
                "v": round(r * h, 6),
                "w": round(w, 6),
                "h": round(h, 6),
            })
    return pieces


def generate(mission: Mission, image_url: str, piece_count: int = 12) -> JigsawPuzzle:
    cols, rows = _grid_for(piece_count)
    puzzle, _ = JigsawPuzzle.objects.update_or_create(
        mission=mission,
        defaults=dict(
            image_url=image_url,
            piece_count=cols * rows,
            grid_cols=cols,
            grid_rows=rows,
            piece_data=build_grid_pieces(cols, rows),
        ),
    )
    return puzzle
