import type { ExtractionField } from "@/entities/extraction"
import { useErrorText, useTranslation } from "@/shared/i18n"
import { Button, Card, EmptyState, ErrorState, Icon, Skeleton } from "@/shared/ui"
import { exportCard } from "../export-card"
import { FieldResults } from "../field-results/field-results"
import type { ReviewActionsProps } from "../review-actions/review-contract"
import type { useExtraction } from "../use-extraction"
import styles from "./extraction-results.module.css"

export interface ExtractionResultsProps
  extends Omit<ReviewActionsProps, "field" | "category" | "sourceText"> {
  readonly extraction: ReturnType<typeof useExtraction>
  readonly onRun: (categoryId?: number) => void
  readonly onQuote: (field: ExtractionField) => void
}

function ResultStatus({ extraction }: Pick<ExtractionResultsProps, "extraction">) {
  const { t } = useTranslation()
  const fields = extraction.event?.fields ?? []
  if (extraction.isPending) return t("home:extraction.processing")
  if (extraction.isError) return t("home:extraction.failed")
  if (!extraction.event) return t("home:extraction.ready")
  if (extraction.event.category_id === null) return t("home:extraction.chooseCategory")
  return t("home:extraction.summary", {
    accepted: fields.filter((field) => field.state === "accepted").length,
    review: fields.filter((field) => field.state === "review").length,
  })
}

export function ExtractionResults({
  extraction,
  onRun,
  onQuote,
  ...actions
}: ExtractionResultsProps) {
  const { t } = useTranslation()
  const errorText = useErrorText()
  const event = extraction.event
  const fields = event?.fields ?? []
  const complete = event?.stage === "complete" && !extraction.isError
  const canExport = complete && fields.some((field) => field.state === "accepted")
  return (
    <Card
      title={t("home:extraction.outputTitle")}
      actions={
        canExport && event ? (
          <Button icon="download" variant="secondary" onClick={() => exportCard(event)}>
            {t("home:extraction.export")}
          </Button>
        ) : undefined
      }
    >
      <p role="status" aria-live="polite" className={styles.progress}>
        <ResultStatus extraction={extraction} />
      </p>
      {extraction.isError ? (
        <ErrorState title={errorText(extraction.error)} onRetry={() => onRun()} />
      ) : null}
      {extraction.isPending ? <Skeleton /> : null}
      {extraction.isIdle ? (
        <EmptyState
          icon="document"
          title={t("home:extraction.emptyTitle")}
          description={t("home:extraction.emptyHint")}
        />
      ) : null}
      {event ? (
        <p className={styles.category} lang="ru">
          {event.category_name}
        </p>
      ) : null}
      {complete && event?.category_id === null ? (
        <div className={styles.categories}>
          {event.categories?.map((category) => (
            <Button
              key={category.category_id}
              icon="document"
              variant="secondary"
              onClick={() => onRun(category.category_id)}
            >
              <span lang="ru">{category.name}</span>
            </Button>
          ))}
        </div>
      ) : null}
      {event?.warning ? (
        <p className={styles.notice}>
          <Icon name="alert" size="sm" />
          {t("home:extraction.fallback")}
        </p>
      ) : null}
      <FieldResults
        fields={fields}
        onQuote={onQuote}
        category={event?.category_name ?? ""}
        sourceText={event?.source_text ?? ""}
        {...actions}
      />
      {event?.synthetic_catalog ? (
        <p className={styles.notice}>{t("home:extraction.synthetic")}</p>
      ) : null}
    </Card>
  )
}
