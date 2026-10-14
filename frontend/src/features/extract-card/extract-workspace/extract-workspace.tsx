import { useState } from "react"
import type { ExtractionField } from "@/entities/extraction"
import { useErrorText, useTranslation } from "@/shared/i18n"
import { Button, Card, ErrorState, Textarea } from "@/shared/ui"
import { ExtractionResults } from "../extraction-results/extraction-results"
import type { FieldOption } from "../review-actions/review-contract"
import { SourceEvidence } from "../source-evidence/source-evidence"
import { useExtraction } from "../use-extraction"
import { useFeedback } from "../use-feedback"
import styles from "./extract-workspace.module.css"

export function ExtractWorkspace() {
  const { t } = useTranslation()
  const [text, setText] = useState("")
  const [quote, setQuote] = useState<ExtractionField>()
  const extraction = useExtraction()
  const event = extraction.event
  const errorText = useErrorText()
  const refresh = () => {
    if (event?.category_id)
      extraction.mutate({ text: event.source_text, category_id: event.category_id })
  }
  const feedback = useFeedback(refresh)
  const choose = (field: ExtractionField, option: FieldOption, learn: boolean) => {
    if (!event?.category_id) return
    feedback.mutate({
      kind: "save",
      body: {
        request_id: crypto.randomUUID(),
        text: event.source_text,
        category_id: event.category_id,
        attribute: field.attribute,
        value: option.value,
        quote: option.quote,
        start: option.start,
        end: option.end,
        learn_alias: learn,
      },
    })
  }
  const revoke = (field: ExtractionField) => {
    if (field.correction_id && field.correction_version)
      feedback.mutate({
        kind: "revoke",
        id: field.correction_id,
        version: field.correction_version,
      })
  }
  const run = (categoryId?: number) => {
    setQuote(undefined)
    extraction.mutate({ text, ...(categoryId === undefined ? {} : { category_id: categoryId }) })
  }
  return (
    <div className={styles.workspace}>
      <Card title={t("home:extraction.inputTitle")}>
        <form
          className={styles.form}
          onSubmit={(submit) => {
            submit.preventDefault()
            run()
          }}
        >
          <Textarea
            label={t("home:extraction.inputLabel")}
            hint={t("home:extraction.inputHint")}
            value={text}
            onChange={(change) => {
              feedback.reset()
              setText(change.target.value)
              extraction.clear()
              setQuote(undefined)
            }}
            rows={10}
            maxLength={30000}
            required
            disabled={extraction.isPending || feedback.isPending}
          />
          <Button
            type="submit"
            icon="extract"
            pending={extraction.isPending}
            disabled={!text.trim() || feedback.isPending}
          >
            {t("home:extraction.run")}
          </Button>
        </form>
        {quote && event ? <SourceEvidence quote={quote} text={event.source_text} /> : null}
      </Card>
      <div className={styles.results}>
        {feedback.isError ? (
          <ErrorState
            title={errorText(feedback.error)}
            onRetry={() => {
              if (feedback.variables) feedback.mutate(feedback.variables)
            }}
          />
        ) : null}
        {feedback.isPending ? <p role="status">{t("home:feedback.saving")}</p> : null}
        <ExtractionResults
          extraction={extraction}
          onRun={run}
          onQuote={setQuote}
          pending={feedback.isPending || extraction.isPending}
          onChoose={choose}
          onRevoke={revoke}
        />
      </div>
    </div>
  )
}
