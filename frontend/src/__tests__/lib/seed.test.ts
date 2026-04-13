import { SEED_TODAY, SEED_MISSION } from "../../lib/seed";

describe("SEED_TODAY", () => {
  it("has required shape", () => {
    expect(SEED_TODAY).toHaveProperty("apod");
    expect(SEED_TODAY).toHaveProperty("mission_slug");
  });

  it("apod has date, title, explanation", () => {
    expect(SEED_TODAY.apod).toHaveProperty("date");
    expect(typeof SEED_TODAY.apod.date).toBe("string");
    expect(SEED_TODAY.apod.date.length).toBeGreaterThan(0);

    expect(SEED_TODAY.apod).toHaveProperty("title");
    expect(typeof SEED_TODAY.apod.title).toBe("string");
    expect(SEED_TODAY.apod.title.length).toBeGreaterThan(0);

    expect(SEED_TODAY.apod).toHaveProperty("explanation");
    expect(typeof SEED_TODAY.apod.explanation).toBe("string");
    expect(SEED_TODAY.apod.explanation.length).toBeGreaterThan(0);
  });

  it("mission_slug is a non-empty string", () => {
    expect(typeof SEED_TODAY.mission_slug).toBe("string");
    expect(SEED_TODAY.mission_slug!.length).toBeGreaterThan(0);
  });
});

describe("SEED_MISSION", () => {
  it("has required shape", () => {
    expect(SEED_MISSION).toHaveProperty("slug");
    expect(typeof SEED_MISSION.slug).toBe("string");

    expect(SEED_MISSION).toHaveProperty("title");
    expect(typeof SEED_MISSION.title).toBe("string");
  });

  it("has quizzes with length 2", () => {
    expect(SEED_MISSION.quizzes).toHaveLength(2);
    SEED_MISSION.quizzes.forEach((q) => {
      expect(q).toHaveProperty("id");
      expect(q).toHaveProperty("question");
      expect(q).toHaveProperty("options");
      expect(q.options.length).toBeGreaterThanOrEqual(2);
      expect(q).toHaveProperty("difficulty");
    });
  });

  it("has jigsaw with 12 pieces", () => {
    expect(SEED_MISSION.jigsaw).not.toBeNull();
    const jigsaw = SEED_MISSION.jigsaw!;
    expect(jigsaw.piece_count).toBe(12);
    expect(jigsaw.piece_data).toHaveLength(12);
  });

  it("jigsaw has correct grid dimensions", () => {
    const jigsaw = SEED_MISSION.jigsaw!;
    expect(jigsaw.grid_cols).toBe(4);
    expect(jigsaw.grid_rows).toBe(3);
  });

  it("jigsaw piece_data covers full grid (12 pieces, 4 cols, 3 rows)", () => {
    const jigsaw = SEED_MISSION.jigsaw!;
    const pieces = jigsaw.piece_data;

    // Every piece has row and col
    pieces.forEach((p) => {
      expect(p).toHaveProperty("id");
      expect(p).toHaveProperty("row");
      expect(p).toHaveProperty("col");
      expect(p).toHaveProperty("u");
      expect(p).toHaveProperty("v");
      expect(p).toHaveProperty("w");
      expect(p).toHaveProperty("h");
    });

    // Verify all grid positions are covered
    const positions = new Set(pieces.map((p) => `${p.row},${p.col}`));
    expect(positions.size).toBe(12);

    for (let row = 0; row < 3; row++) {
      for (let col = 0; col < 4; col++) {
        expect(positions.has(`${row},${col}`)).toBe(true);
      }
    }
  });

  it("jigsaw pieces have valid UV coordinates", () => {
    const jigsaw = SEED_MISSION.jigsaw!;
    jigsaw.piece_data.forEach((p) => {
      expect(p.u).toBeGreaterThanOrEqual(0);
      expect(p.u).toBeLessThan(1);
      expect(p.v).toBeGreaterThanOrEqual(0);
      expect(p.v).toBeLessThan(1);
      expect(p.w).toBeGreaterThan(0);
      expect(p.h).toBeGreaterThan(0);
    });
  });
});
