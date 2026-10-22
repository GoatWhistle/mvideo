export interface Thread {
  readonly key: string
  readonly path: string
  readonly startX: number
  readonly startY: number
  readonly endX: number
  readonly endY: number
}

export interface ThreadMetrics {
  readonly lead: number
  readonly rowAnchor: number
  readonly radius: number
}

const LANE = "[data-thread-lane]"

function clamp(value: number, low: number, high: number): number {
  return Math.min(Math.max(value, low), Math.max(low, high))
}

function byKey(root: HTMLElement, attribute: string, key: string): HTMLElement | undefined {
  return [...root.querySelectorAll<HTMLElement>(`[${attribute}]`)].find(
    (element) => element.getAttribute(attribute) === key,
  )
}

function round(value: number): number {
  return Math.round(value * 10) / 10
}

export function routePath(
  fromX: number,
  fromY: number,
  toX: number,
  toY: number,
  radius: number,
): string {
  const midX = (fromX + toX) / 2
  const rise = toY - fromY
  const across = Math.sign(toX - fromX)
  const down = Math.sign(rise)
  const r = Math.min(radius, Math.abs(rise) / 2, Math.abs(midX - fromX))
  return [
    `M ${round(fromX)} ${round(fromY)}`,
    `H ${round(midX - across * r)}`,
    `Q ${round(midX)} ${round(fromY)} ${round(midX)} ${round(fromY + down * r)}`,
    `V ${round(toY - down * r)}`,
    `Q ${round(midX)} ${round(toY)} ${round(midX + across * r)} ${round(toY)}`,
    `H ${round(toX)}`,
  ].join(" ")
}

export function measureThread(root: HTMLElement, key: string, metrics: ThreadMetrics) {
  const source = byKey(root, "data-thread-source", key)
  const target = byKey(root, "data-thread-target", key)
  const sourceLane = source?.closest(LANE)
  const targetLane = target?.closest(LANE)
  if (!source || !target || !sourceLane || !targetLane) return null
  const box = root.getBoundingClientRect()
  const line = target.getClientRects()[0] ?? target.getBoundingClientRect()
  const row = source.getBoundingClientRect()
  const lane = targetLane.getBoundingClientRect()
  const rowLane = sourceLane.getBoundingClientRect()
  const direction = lane.right <= rowLane.left ? 1 : lane.left >= rowLane.right ? -1 : 0
  if (direction === 0) return null
  const fromX = (direction === 1 ? lane.right : lane.left) - box.left
  const scroll = target.closest("[data-evidence-scroll]")?.getBoundingClientRect() ?? lane
  const fromY = clamp(
    line.top + line.height / 2 - box.top,
    scroll.top - box.top + metrics.rowAnchor,
    scroll.bottom - box.top - metrics.rowAnchor,
  )
  const toX = (direction === 1 ? rowLane.left : rowLane.right) - box.left
  const toY = row.top + row.height / 2 - box.top
  if (Math.abs(toX - fromX) < metrics.lead) return null
  const thread: Thread = {
    key,
    path: routePath(fromX, fromY, toX, toY, metrics.radius),
    startX: round(fromX),
    startY: round(fromY),
    endX: round(toX),
    endY: round(toY),
  }
  return thread
}
