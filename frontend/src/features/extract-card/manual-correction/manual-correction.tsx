import { useRef, useState } from "react"
import { useTranslation } from "@/shared/i18n"
import { Button, TextField } from "@/shared/ui"
import type { ReviewActionsProps } from "../review-actions/review-contract"
import styles from "./manual-correction.module.css"

export function ManualCorrection({
  field,
  sourceText,
  category,
  pending,
  onChoose,
}: ReviewActionsProps) {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const [value, setValue] = useState("")
  const [quote, setQuote] = useState(field.quote ?? "")
  const [error, setError] = useState(false)
  const form = useRef<HTMLFormElement>(null)
  const save = (learn: boolean) => {
    if (!form.current?.reportValidity()) return
    const offset = sourceText.indexOf(quote)
    if (offset < 0) {
      setError(true)
      return
    }
    const start = Array.from(sourceText.slice(0, offset)).length
    onChoose(field, { value, quote, start, end: start + Array.from(quote).length }, learn)
  }
  if (!open)
    return (
      <Button icon="edit" variant="ghost" disabled={pending} onClick={() => setOpen(true)}>
        {t("home:feedback.manual")}
      </Button>
    )
  return (
    <form
      ref={form}
      className={styles.form}
      onSubmit={(event) => {
        event.preventDefault()
        save(false)
      }}
    >
      <TextField
        label={t("home:feedback.value")}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        required
        maxLength={200}
        disabled={pending}
      />
      <TextField
        label={t("home:feedback.quote")}
        value={quote}
        onChange={(event) => {
          setQuote(event.target.value)
          setError(false)
        }}
        required
        maxLength={500}
        disabled={pending}
      />
      {error ? <p role="alert">{t("home:feedback.quoteMissing")}</p> : null}
      {field.alias_brand ? (
        <p className={styles.scope}>
          {t("home:feedback.scope", {
            category,
            brand: field.alias_brand,
            attribute: field.attribute,
          })}
        </p>
      ) : null}
      <div className={styles.buttons}>
        <Button type="submit" icon="success" disabled={pending}>
          {t("home:feedback.saveHere")}
        </Button>
        {field.alias_brand ? (
          <Button icon="save" variant="secondary" disabled={pending} onClick={() => save(true)}>
            {t("home:feedback.saveLearn")}
          </Button>
        ) : null}
        <Button icon="retry" variant="ghost" onClick={() => setOpen(false)}>
          {t("home:feedback.cancel")}
        </Button>
      </div>
    </form>
  )
}
