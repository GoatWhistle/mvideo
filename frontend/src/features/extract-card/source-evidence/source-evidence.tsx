import { useEffect, useRef } from "react"
import type { ExtractionField } from "@/entities/extraction"
import { useTranslation } from "@/shared/i18n"
import styles from "./source-evidence.module.css"

export interface SourceEvidenceProps {
  readonly quote: ExtractionField
  readonly text: string
}

export function SourceEvidence({ quote, text }: SourceEvidenceProps) {
  const { t } = useTranslation()
  const source = useRef<HTMLParagraphElement>(null)
  useEffect(() => {
    if (quote.start === null) return
    source.current?.scrollIntoView({ block: "nearest" })
    source.current?.focus({ preventScroll: true })
  }, [quote])
  const chars = Array.from(text)
  return (
    <div className={styles.evidence}>
      <p>{t("home:extraction.evidence")}</p>
      <p ref={source} tabIndex={-1} className={styles.source} lang="ru">
        {chars.slice(0, quote.start ?? 0).join("")}
        <mark>{chars.slice(quote.start ?? 0, quote.end ?? 0).join("")}</mark>
        {chars.slice(quote.end ?? 0).join("")}
      </p>
    </div>
  )
}
