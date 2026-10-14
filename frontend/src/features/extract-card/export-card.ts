import type { ExtractionEvent } from "@/entities/extraction"

export function exportCard(event: ExtractionEvent) {
  const payload = {
    category_id: event.category_id,
    source_text: event.source_text,
    catalog_version: event.catalog_version,
    synthetic_catalog: event.synthetic_catalog,
    execution: {
      elapsed_ms: event.elapsed_ms,
      model_calls: event.model_calls,
      model_usage: event.model_usage,
      cached: event.cached,
    },
    fields: event.fields?.filter((field) => field.state === "accepted"),
    unresolved: event.fields?.filter((field) => field.state !== "accepted"),
  }
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }),
  )
  const link = document.createElement("a")
  link.href = url
  link.download = "product-card.json"
  link.click()
  URL.revokeObjectURL(url)
}
