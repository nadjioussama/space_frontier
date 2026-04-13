import { API_BASE, resolveAsset, apiFetch, ApiError } from "../../lib/api";

describe("API_BASE", () => {
  it("defaults to localhost:8000", () => {
    expect(API_BASE).toBe("http://localhost:8000");
  });
});

describe("resolveAsset", () => {
  it("returns empty string for empty input", () => {
    expect(resolveAsset("")).toBe("");
  });

  it("returns empty string for null", () => {
    expect(resolveAsset(null)).toBe("");
  });

  it("returns empty string for undefined", () => {
    expect(resolveAsset(undefined)).toBe("");
  });

  it("returns absolute http URLs unchanged", () => {
    const url = "http://example.com/image.jpg";
    expect(resolveAsset(url)).toBe(url);
  });

  it("returns absolute https URLs unchanged", () => {
    const url = "https://cdn.nasa.gov/apod/image.jpg";
    expect(resolveAsset(url)).toBe(url);
  });

  it("returns /seed/ paths unchanged", () => {
    expect(resolveAsset("/seed/starfield.svg")).toBe("/seed/starfield.svg");
  });

  it("returns /_next/ paths unchanged", () => {
    expect(resolveAsset("/_next/static/image.png")).toBe("/_next/static/image.png");
  });

  it("prepends API_BASE to relative paths starting with /", () => {
    expect(resolveAsset("/media/apod/image.jpg")).toBe(
      `${API_BASE}/media/apod/image.jpg`
    );
  });

  it("returns non-slash relative paths as-is", () => {
    expect(resolveAsset("some-file.jpg")).toBe("some-file.jpg");
  });
});

describe("ApiError", () => {
  it("has status and message properties", () => {
    const err = new ApiError(404, "Not Found");
    expect(err.status).toBe(404);
    expect(err.message).toBe("Not Found");
  });

  it("is an instance of Error", () => {
    const err = new ApiError(500, "Server Error");
    expect(err).toBeInstanceOf(Error);
  });
});

describe("apiFetch", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    globalThis.fetch = jest.fn();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("calls fetch with correct URL", async () => {
    (globalThis.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ data: "ok" }),
    });
    await apiFetch("/api/v1/today/");
    expect(globalThis.fetch).toHaveBeenCalledWith(
      `${API_BASE}/api/v1/today/`,
      expect.objectContaining({
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
      })
    );
  });

  it("includes Content-Type header", async () => {
    (globalThis.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    });
    await apiFetch("/test");
    const callArgs = (globalThis.fetch as jest.Mock).mock.calls[0];
    expect(callArgs[1].headers["Content-Type"]).toBe("application/json");
  });

  it("merges custom headers", async () => {
    (globalThis.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    });
    await apiFetch("/test", {
      headers: { Authorization: "Bearer token123" },
    });
    const callArgs = (globalThis.fetch as jest.Mock).mock.calls[0];
    expect(callArgs[1].headers["Authorization"]).toBe("Bearer token123");
    expect(callArgs[1].headers["Content-Type"]).toBe("application/json");
  });

  it("parses JSON response", async () => {
    const payload = { apod: { date: "2024-01-01" }, mission_slug: "m1" };
    (globalThis.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(payload),
    });
    const result = await apiFetch("/api/v1/today/");
    expect(result).toEqual(payload);
  });

  it("throws ApiError on non-2xx response", async () => {
    (globalThis.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      text: () => Promise.resolve("resource not found"),
    });
    await expect(apiFetch("/api/v1/missing/")).rejects.toThrow(ApiError);
    await expect(apiFetch("/api/v1/missing/")).rejects.toMatchObject({
      status: 404,
      message: "resource not found",
    });
  });

  it("uses statusText when text() is empty", async () => {
    (globalThis.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      text: () => Promise.resolve(""),
    });
    await expect(apiFetch("/api/v1/broken/")).rejects.toMatchObject({
      status: 500,
      message: "Internal Server Error",
    });
  });
});
