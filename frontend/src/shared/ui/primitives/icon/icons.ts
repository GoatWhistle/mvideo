import {
  CircleCheck,
  Download,
  FileText,
  House,
  Inbox,
  LoaderCircle,
  type LucideProps,
  Moon,
  Pencil,
  Quote,
  RefreshCw,
  RotateCcw,
  Save,
  Sparkles,
  Sun,
  TriangleAlert,
} from "lucide-react"
import type { ComponentType } from "react"

export const ICONS = {
  alert: TriangleAlert,
  download: Download,
  document: FileText,
  quote: Quote,
  extract: Sparkles,
  save: Save,
  edit: Pencil,
  success: CircleCheck,
  empty: Inbox,
  home: House,
  loader: LoaderCircle,
  refresh: RefreshCw,
  retry: RotateCcw,
  "theme-light": Sun,
  "theme-dark": Moon,
} as const satisfies Record<string, ComponentType<LucideProps>>

export type IconName = keyof typeof ICONS
