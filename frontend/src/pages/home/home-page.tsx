import { ExtractWorkspace } from "@/features/extract-card"
import { useDocumentTitle, useTranslation } from "@/shared/i18n"
import { PageHeader } from "@/shared/ui"
import styles from "./home-page.module.css"

export function HomePage() {
  const { t } = useTranslation()
  useDocumentTitle(null)
  return (
    <div className={styles.page}>
      <PageHeader title={t("home:title")} description={t("home:description")} />
      <ExtractWorkspace />
    </div>
  )
}
