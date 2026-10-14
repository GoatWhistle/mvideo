import type { ExtractionField } from "@/entities/extraction"
import { useTranslation } from "@/shared/i18n"
import styles from "./field-results.module.css"

function sourceKey(source: string) {
  switch (source) {
    case "dictionary":
    case "decision_model":
    case "human":
    case "confirmed_alias":
      return source
    default:
      return "rule"
  }
}

export function FieldProvenance({ field }: { readonly field: ExtractionField }) {
  const { t } = useTranslation()
  if (!field.source) return null
  const calibration =
    field.score_kind === "human_confirmation"
      ? t("home:provenance.human")
      : field.confidence === null
        ? t("home:provenance.uncalibrated")
        : t("home:provenance.calibrated", { value: field.confidence })
  return (
    <p className={styles.reason}>
      {t("home:provenance.source", {
        source: t(`home:provenance.sources.${sourceKey(field.source)}`),
      })}
      <br />
      {calibration}
    </p>
  )
}
