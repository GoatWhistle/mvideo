import type { ExtractionField } from "@/entities/extraction"

export type FieldOption = ExtractionField["alternatives"][number]
export interface ReviewActionsProps {
  readonly field: ExtractionField
  readonly category: string
  readonly sourceText: string
  readonly pending: boolean
  readonly onChoose: (field: ExtractionField, option: FieldOption, learn: boolean) => void
  readonly onRevoke: (field: ExtractionField) => void
}
