import { useMutation } from "@tanstack/react-query"
import { useEffect, useRef, useState } from "react"
import { type ExtractionEvent, type ExtractRequest, extractCard } from "@/entities/extraction"

export function useExtraction() {
  const [event, setEvent] = useState<ExtractionEvent>()
  const controller = useRef<AbortController | null>(null)
  const mutation = useMutation({
    mutationFn: async (body: ExtractRequest) => {
      controller.current?.abort()
      const active = new AbortController()
      controller.current = active
      setEvent(undefined)
      return extractCard(body, active.signal, (next) => {
        if (!active.signal.aborted) setEvent(next)
      })
    },
    retry: false,
  })
  useEffect(() => () => controller.current?.abort(), [])
  return {
    ...mutation,
    event,
    clear: () => {
      controller.current?.abort()
      setEvent(undefined)
      mutation.reset()
    },
  }
}
