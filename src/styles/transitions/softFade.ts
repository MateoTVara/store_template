import type { TransitionConfig } from "svelte/transition";
import { cubicInOut } from "svelte/easing";

interface Options {
  duration?: number;
  start?: number;
  easing?: (t: number) => number;
}

export default function softFade(
  node: Element,
  { duration = 300, start = 0.4, easing = cubicInOut }: Options = {}
): TransitionConfig {
  if (start < 0 || start > 1) {
    throw new Error("start value must be between 0 and 1");
  }

  return {
    duration,
    easing,
    css: (t) => {
      const opacity = start + (1 - start) * t;
      return `opacity: ${opacity}`;
    }
  };
}