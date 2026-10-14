import type { ExtractionField } from "@/entities/extraction"
import { useTranslation } from "@/shared/i18n"
import { Button, Icon, type IconName, NoValue } from "@/shared/ui"
import { ReviewActions } from "../review-actions/review-actions"
import type { ReviewActionsProps } from "../review-actions/review-contract"
import { FieldProvenance } from "./field-provenance"
import styles from "./field-results.module.css"

const STATUS_ICON: Record<ExtractionField["state"], IconName> = {
  accepted: "success",
  review: "alert",
  not_stated: "empty",
  unsupported: "alert",
}

export interface FieldResultsProps extends Omit<ReviewActionsProps, "field"> {
  readonly fields: readonly ExtractionField[]
  readonly onQuote: (field: ExtractionField) => void
}

export function FieldResults({ fields, onQuote, ...actions }: FieldResultsProps) {
  const { t } = useTranslation()
  return (
    <dl className={styles.fields}>
      {fields.map((field) => (
        <div key={field.attribute} className={styles.row} data-state={field.state}>
          <dt className={styles.name} lang="ru">
            {field.attribute}
          </dt>
          <dd className={styles.detail}>
            <div className={styles.value} lang="ru">
              {field.value ?? <NoValue />}
            </div>
            <span className={styles.status}>
              <Icon name={STATUS_ICON[field.state]} size="sm" />
              {t(`home:extraction.states.${field.state}`)}
            </span>
            {field.quote ? (
              <Button icon="quote" variant="ghost" onClick={() => onQuote(field)}>
                <span className={styles.quote} lang="ru">
                  {field.quote}
                </span>
              </Button>
            ) : null}
            {field.state === "review" ? (
              <p className={styles.reason}>{t("home:extraction.reviewHint")}</p>
            ) : null}
            <FieldProvenance field={field} />
            <ReviewActions {...actions} field={field} />
          </dd>
        </div>
      ))}
    </dl>
  )
}
