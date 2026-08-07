"use client";

import { motion, useReducedMotion, useScroll, useSpring, useTransform, type MotionValue } from "framer-motion";
import { useRef, type ReactNode } from "react";
import { cn } from "@/lib/utils";

const SPRING = { stiffness: 120, damping: 28, mass: 0.45 };

interface ScrollSceneValues {
  progress: MotionValue<number>;
  smoothProgress: MotionValue<number>;
  reducedMotion: boolean;
}

export function ScrollScene({ children, className, id }: { children: (values: ScrollSceneValues) => ReactNode; className?: string; id?: string }) {
  const ref = useRef<HTMLElement>(null);
  const reducedMotion = useReducedMotion() ?? false;
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const smoothProgress = useSpring(scrollYProgress, SPRING);
  return <section ref={ref} id={id} className={cn("relative [perspective:1200px]", className)}>{children({ progress: scrollYProgress, smoothProgress, reducedMotion })}</section>;
}

export function ScrollReveal3D({ children, className, depth = 80, rotateX = 4, delay = 0 }: { children: ReactNode; className?: string; depth?: number; rotateX?: number; delay?: number }) {
  const reducedMotion = useReducedMotion();
  return <motion.div initial={reducedMotion ? { opacity: 0 } : { opacity: 0, y: 32, scale: 0.96, rotateX, z: -depth }} whileInView={{ opacity: 1, y: 0, scale: 1, rotateX: 0, z: 0 }} viewport={{ once: true, margin: "-10%" }} transition={{ duration: reducedMotion ? 0.2 : 0.7, delay, ease: [0.22, 1, 0.36, 1] }} className={cn("[transform-style:preserve-3d]", className)}>{children}</motion.div>;
}

export function DepthCard({ children, className, index = 0 }: { children: ReactNode; className?: string; index?: number }) {
  const reducedMotion = useReducedMotion();
  const depth = Math.min(index, 4) * 18;
  return <motion.div initial={reducedMotion ? { opacity: 0 } : { opacity: 0, y: 28, scale: 0.96, z: -70 - depth }} whileInView={{ opacity: 1, y: 0, scale: 1, z: 0 }} viewport={{ once: true, margin: "-8%" }} transition={{ delay: reducedMotion ? 0 : index * 0.08, duration: 0.6, ease: [0.22, 1, 0.36, 1] }} whileHover={reducedMotion ? undefined : { scale: 1.02, rotateX: -2, rotateY: index % 2 ? -3 : 3 }} className={cn("[transform-style:preserve-3d] motion-reduce:transform-none", className)}>{children}</motion.div>;
}

export { useTransform };
