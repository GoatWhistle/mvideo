import { ApiError, api, type components, unwrap } from "@/shared/api"

export type ExtractionEvent = components["schemas"]["ExtractionEventSchema"]
export type ExtractionField = components["schemas"]["FieldSchema"]
export type ExtractRequest =
  components["schemas"]["app__controller__extraction__schemas__ExtractRequest"]

function parseEvent(line: string): ExtractionEvent {
  const event: ExtractionEvent = JSON.parse(line)
  if (!["category", "rules", "complete"].includes(event.stage)) {
    throw new ApiError(502, "unexpected")
  }
  return event
}

async function* readEvents(stream: ReadableStream<Uint8Array>) {
  const reader = stream.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  try {
    while (true) {
      const { done, value } = await reader.read()
      buffer += decoder.decode(value, { stream: !done })
      const lines = buffer.split("\n")
      buffer = lines.pop() ?? ""
      if (done && buffer.trim()) lines.push(buffer)
      for (const line of lines) {
        if (line.trim()) yield parseEvent(line)
      }
      if (done) break
    }
  } finally {
    await reader.cancel().catch(() => undefined)
    reader.releaseLock()
  }
}

export async function extractCard(
  body: ExtractRequest,
  signal: AbortSignal,
  onEvent: (event: ExtractionEvent) => void,
): Promise<ExtractionEvent> {
  const stream = await unwrap(
    api.POST("/api/v1/extract/stream", { body, signal, parseAs: "stream" }),
  )
  if (!stream) throw new ApiError(502, "unexpected")
  let latest: ExtractionEvent | undefined
  for await (const event of readEvents(stream)) {
    latest = event
    onEvent(event)
  }
  if (latest?.stage !== "complete") throw new ApiError(502, "unexpected")
  return latest
}
