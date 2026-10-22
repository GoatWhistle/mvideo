import { useCallback, useRef, useState } from "react"
import { usePresence, withViewTransition } from "@/shared/motion"

export function useEvidenceDisclosure() {
  const [focused, setFocused] = useState<string | null>(null)
  const [open, setOpen] = useState(false)
  const [instant, setInstant] = useState(false)
  const keyboardOpened = useRef(false)
  const shown = useRef(false)
  const panel = usePresence(open, "--dur-drawer-exit", instant)
  const change = useCallback((next: boolean, keyboard: boolean, attribute: string | null) => {
    const toggles = shown.current !== next
    shown.current = next
    const snapshot = toggles && !keyboard && typeof document.startViewTransition === "function"
    const update = () => {
      if (toggles) setInstant(keyboard || snapshot)
      if (next) setFocused(attribute)
      setOpen(next)
    }
    if (snapshot) void withViewTransition(next ? "evidence-open" : "evidence-close", update)
    else update()
  }, [])
  const close = useCallback(
    (keyboard = keyboardOpened.current) => change(false, keyboard, null),
    [change],
  )
  const show = (attribute: string | null, keyboard: boolean) => {
    keyboardOpened.current = keyboard
    change(true, keyboard, attribute)
  }
  return { focused, open, instant, panel, close, show }
}
