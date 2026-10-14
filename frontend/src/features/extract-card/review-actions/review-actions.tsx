import { useTranslation } from "@/shared/i18n"
import { Button } from "@/shared/ui"
import { ManualCorrection } from "../manual-correction/manual-correction"
import styles from "./review-actions.module.css"
import type { ReviewActionsProps } from "./review-contract"

export function ReviewActions({
  field,
  category,
  pending,
  onChoose,
  onRevoke,
  sourceText,
}: ReviewActionsProps) {
  const { t } = useTranslation()
  if (field.correction_id)
    return (
      <Button icon="retry" variant="ghost" disabled={pending} onClick={() => onRevoke(field)}>
        {t("home:feedback.undo")}
      </Button>
    )
  if (field.state === "not_stated")
    return <ManualCorrection {...{ field, category, pending, onChoose, onRevoke, sourceText }} />
  if (field.state !== "review") return null
  return (
    <div className={styles.actions}>
      {field.alias_brand ? (
        <p className={styles.scope}>
          {t("home:feedback.scope", {
            category,
            brand: field.alias_brand,
            attribute: field.attribute,
          })}
        </p>
      ) : null}
      {field.alternatives.map((option) => (
        <div className={styles.option} key={`${option.value}:${option.start}`}>
          <Button
            className={styles.choice}
            icon="success"
            variant="secondary"
            disabled={pending}
            onClick={() => onChoose(field, option, false)}
          >
            {t("home:feedback.accept", { value: option.value })}
          </Button>
          {field.alias_brand ? (
            <Button
              className={styles.choice}
              icon="save"
              variant="ghost"
              disabled={pending}
              onClick={() => onChoose(field, option, true)}
            >
              {t("home:feedback.learn", { value: option.value })}
            </Button>
          ) : null}
        </div>
      ))}
      <ManualCorrection {...{ field, category, pending, onChoose, onRevoke, sourceText }} />
    </div>
  )
}
