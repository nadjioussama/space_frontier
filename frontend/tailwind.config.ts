import type { Config } from "tailwindcss";
import plugin from "tailwindcss/plugin";

// PLAN §16 — full deep space palette. Phase 6 expanded.
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        space: {
          900: "#0B0D17",    // spaceBlack — primary bg
          800: "#1B2735",    // deepNavy — card/panel bg
          700: "#162447",    // midnightBlue — secondary surfaces
          600: "#1e3a5f",
          accent: "#2E86AB", // cosmicBlue — buttons, links
          "accent-light": "#66d9ff",
          nasa: "#105BD8",   // official NASA blue
          purple: "#7B2D8E", // nebulaPurple — discovery moments
          rust: "#C1440E",   // marsRust — Mars content
          gold: "#F0A500",   // solarGold — achievements, rewards
          ok: "#2ECC71",     // auroraGreen — correct answers
          teal: "#1ABC9C",   // cometTeal — secondary interactive
          warn: "#ffb347",
          error: "#E74C3C",
          star: "#E8E8E8",   // starWhite — primary text
          lunar: "#9BA3AF",  // lunarGray — secondary text
        },
      },
      fontFamily: {
        display: ["Orbitron", "system-ui", "sans-serif"],
        body: ["Nunito", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      // Phase 6: animation system tokens (§19)
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 8px rgba(46,134,171,0.3)" },
          "50%": { boxShadow: "0 0 20px rgba(46,134,171,0.6)" },
        },
        "star-twinkle": {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
        "shake": {
          "0%, 100%": { transform: "translateX(0)" },
          "25%": { transform: "translateX(-4px)" },
          "75%": { transform: "translateX(4px)" },
        },
        "badge-drop": {
          "0%": { transform: "translateY(-40px) scale(0.5)", opacity: "0" },
          "60%": { transform: "translateY(4px) scale(1.1)" },
          "100%": { transform: "translateY(0) scale(1)", opacity: "1" },
        },
        "count-up": {
          "0%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.2)" },
          "100%": { transform: "scale(1)" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.3s ease-out",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "star-twinkle": "star-twinkle 3s ease-in-out infinite",
        "shake": "shake 0.4s ease-in-out",
        "badge-drop": "badge-drop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)",
        "count-up": "count-up 0.3s ease-out",
      },
      // Phase 6: glassmorphism surfaces (§18.2)
      backdropBlur: {
        xs: "2px",
      },
      boxShadow: {
        glow: "0 0 15px rgba(46, 134, 171, 0.3)",
        "glow-gold": "0 0 15px rgba(240, 165, 0, 0.4)",
        "glow-ok": "0 0 15px rgba(46, 204, 113, 0.3)",
      },
    },
  },
  plugins: [
    // Age-adaptive utility classes (§18.4)
    plugin(function ({ addUtilities }) {
      addUtilities({
        ".age-6-8": {
          fontSize: "1.125rem",
          lineHeight: "1.75",
        },
        ".age-9-11": {
          fontSize: "1rem",
          lineHeight: "1.625",
        },
        ".age-12-14": {
          fontSize: "0.9375rem",
          lineHeight: "1.5",
        },
      });
    }),
  ],
};

export default config;
