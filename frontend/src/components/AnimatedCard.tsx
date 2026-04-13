"use client";
/**
 * Reusable animated card wrapper. PLAN §19.2.
 * Provides fade-in-up entrance and hover glow.
 */
import { motion, type HTMLMotionProps } from "framer-motion";
import clsx from "clsx";

type Props = HTMLMotionProps<"div"> & {
  delay?: number;
  glow?: boolean;
};

export function AnimatedCard({ delay = 0, glow = false, className, children, ...rest }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3, ease: "easeOut" }}
      whileHover={glow ? { boxShadow: "0 0 16px rgba(46,134,171,0.3)" } : undefined}
      className={clsx("glass-panel p-4 transition-colors", className)}
      {...rest}
    >
      {children}
    </motion.div>
  );
}
