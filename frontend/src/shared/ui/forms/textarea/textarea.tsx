import { type InputHTMLAttributes, type TextareaHTMLAttributes, useId } from "react"
import { Icon } from "../../primitives/icon/icon"
import styles from "./textarea.module.css"

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  readonly label: string
  readonly hint: string
}

export function Textarea({ label, hint, id, ...props }: TextareaProps) {
  const generated = useId()
  const fieldId = id ?? generated
  const hintId = `${fieldId}-hint`
  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={fieldId}>
        <Icon name="document" size="sm" />
        {label}
      </label>
      <textarea {...props} id={fieldId} aria-describedby={hintId} className={styles.input} />
      <p id={hintId} className={styles.hint}>
        {hint}
      </p>
    </div>
  )
}

export interface TextFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  readonly label: string
}

export function TextField({ label, id, ...props }: TextFieldProps) {
  const generated = useId()
  const fieldId = id ?? generated
  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={fieldId}>
        <Icon name="document" size="sm" />
        {label}
      </label>
      <input {...props} id={fieldId} type="text" className={`${styles.input} ${styles.single}`} />
    </div>
  )
}
