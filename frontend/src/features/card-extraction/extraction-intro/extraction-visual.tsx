import { useTranslation } from "@/shared/i18n"
import { type BlueprintProduct, SpecBlueprint } from "@/shared/ui"
import styles from "./extraction-visual.module.css"

const PRODUCTS = ["phone", "laptop", "kettle", "vacuum"] as const
const CALLOUTS = [0, 1, 2, 3] as const

export function ExtractionVisual() {
  const { t } = useTranslation()
  const products: BlueprintProduct[] = PRODUCTS.map((kind) => ({
    kind,
    name: t(`stand:landing.products.${kind}.name`),
    callouts: CALLOUTS.map((index) => ({
      label: t(`stand:landing.products.${kind}.c${index}Label`),
      value: t(`stand:landing.products.${kind}.c${index}Value`),
      quote: t(`stand:landing.products.${kind}.c${index}Quote`),
    })),
  }))
  return (
    <div className={styles.visual}>
      <SpecBlueprint products={products} />
    </div>
  )
}
