import "@testing-library/jest-dom";
import React from "react";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn(), replace: jest.fn(), back: jest.fn(), prefetch: jest.fn() }),
  useParams: () => ({}),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/",
}));

// Mock next/dynamic
jest.mock("next/dynamic", () => ({
  __esModule: true,
  default: (loader: () => Promise<any>) => {
    const Component = (props: any) => null;
    Component.displayName = "DynamicComponent";
    return Component;
  },
}));

// Mock next/link
jest.mock("next/link", () => ({
  __esModule: true,
  default: ({ children, href, ...props }: any) => React.createElement("a", { href, ...props }, children),
}));

// Mock framer-motion
jest.mock("framer-motion", () => {
  const React = require("react");
  
  const motionProps = new Set([
    "initial", "animate", "transition", "exit", "variants", "viewport", 
    "layout", "layoutId", "drag", "dragConstraints", "dragElastic", 
    "dragMomentum", "dragPropagation", "dragTransition", "inherit", 
    "static", "custom", "onUpdate", "onAnimationStart", 
    "onAnimationComplete", "onLayoutAnimationStart", "onLayoutAnimationComplete",
    "onDragStart", "onDragEnd", "onDrag", "onDirectionLock", 
    "onDragTransitionEnd", "onPan", "onPanStart", "onPanSessionStart", 
    "onPanEnd", "onTap", "onTapStart", "onTapCancel", "onHoverStart", "onHoverEnd"
  ]);

  const filterProps = (props: any) => {
    const filtered: any = {};
    Object.keys(props).forEach(key => {
      if (!motionProps.has(key) && !key.startsWith("while")) {
        filtered[key] = props[key];
      }
    });
    return filtered;
  };

  const cache = new Map<string, any>();
  const motion: any = new Proxy({}, {
    get: (_target, tag: string) => {
      if (!cache.has(tag)) {
        const Component = React.forwardRef(({ children, ...props }: any, ref: any) => {
          return React.createElement(tag, { ...filterProps(props), ref }, children);
        });
        Component.displayName = `motion.${tag}`;
        cache.set(tag, Component);
      }
      return cache.get(tag);
    }
  });

  return {
    motion,
    AnimatePresence: ({ children }: any) => children,
    useAnimation: () => ({
      start: jest.fn().mockResolvedValue(undefined),
      set: jest.fn(),
      stop: jest.fn(),
    }),
    useInView: () => true,
    useScroll: () => ({ scrollY: { get: () => 0 }, scrollYProgress: { get: () => 0 } }),
    useTransform: (val: any) => val,
    useSpring: (val: any) => val,
  };
});

// Mock idb-keyval
jest.mock("idb-keyval", () => {
  const store = new Map<string, unknown>();
  return {
    get: jest.fn((key: string) => Promise.resolve(store.get(key))),
    set: jest.fn((key: string, val: unknown) => { store.set(key, val); return Promise.resolve(); }),
    del: jest.fn((key: string) => { store.delete(key); return Promise.resolve(); }),
    keys: jest.fn(() => Promise.resolve([...store.keys()])),
    __store: store,
  };
});

// Mock AudioContext
class MockAudioContext {
  state = "running";
  createOscillator() {
    return {
      type: "sine",
      frequency: { setValueAtTime: jest.fn() },
      connect: jest.fn(),
      start: jest.fn(),
      stop: jest.fn(),
    };
  }
  createGain() {
    return {
      gain: { setValueAtTime: jest.fn(), exponentialRampToValueAtTime: jest.fn() },
      connect: jest.fn(),
    };
  }
  get destination() { return {}; }
  get currentTime() { return 0; }
  resume() { return Promise.resolve(); }
}
(globalThis as any).AudioContext = MockAudioContext;
(globalThis as any).webkitAudioContext = MockAudioContext;

// Mock crypto.randomUUID
Object.defineProperty(globalThis, "crypto", {
  value: { randomUUID: () => "00000000-0000-4000-8000-000000000000" },
});

// Mock localStorage
const localStore = new Map<string, string>();
Object.defineProperty(window, "localStorage", {
  value: {
    getItem: (key: string) => localStore.get(key) ?? null,
    setItem: (key: string, value: string) => localStore.set(key, value),
    removeItem: (key: string) => localStore.delete(key),
    clear: () => localStore.clear(),
  },
});

// Clear between tests
beforeEach(() => {
  localStore.clear();
  jest.clearAllMocks();
});
