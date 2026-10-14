import { useState } from "react"
import { CardExtraction } from "@/features/card-extraction"
import { ReviewQueue } from "@/features/review-queue"
import { useDocumentTitle, useTranslation } from "@/shared/i18n"
import { PageHeader } from "@/shared/ui"
import styles from "./stand-page.module.css"

export function StandPage() {
  const { t } = useTranslation()
  const [refreshKey, setRefreshKey] = useState(0)
  useDocumentTitle(null)
  return (
    <div className={styles.page}>
      <PageHeader title={t("stand:title")} description={t("stand:description")} />
      <CardExtraction
        refreshKey={refreshKey}
        sideSlot={<ReviewQueue onResolved={() => setRefreshKey((key) => key + 1)} />}
      />
    </div>
  )
}
