import nextJest from "next/jest";

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: "./",
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.tsx"],
  testEnvironment: "jsdom",
  moduleNameMapper: {
    // Handle module aliases (this will be automatically configured for you soon)
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  transformIgnorePatterns: ["/node_modules/(?!(idb-keyval)/)"],
  collectCoverage: true,
  coverageDirectory: "coverage",
  coverageReporters: ["text", "lcov", "json", "html"],
  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/**/__tests__/**",
    "!src/setupTests.tsx",
  ],
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
export default createJestConfig(customJestConfig);
