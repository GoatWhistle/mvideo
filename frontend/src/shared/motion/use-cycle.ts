import { useEffect, useState } from "react"
import { motionMs } from "./css-tokens"
import { prefersReducedMotion } from "./use-reduced-motion"

export function useCycle(count: number, beats = 1): number {
  const [index, setIndex] = useState(0)
  useEffect(() => {
    if (count < 2 || prefersReducedMotion()) return
    const timer = window.setInterval(
      () => setIndex((current) => (current + 1) % count),
      motionMs("--dur-breathe") * beats,
    )
    return () => window.clearInterval(timer)
  }, [count, beats])
  return index
}
