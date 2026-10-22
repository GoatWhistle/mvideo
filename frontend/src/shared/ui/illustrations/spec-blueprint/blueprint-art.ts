export type ProductKind = "phone" | "laptop" | "kettle" | "vacuum"

export const BLUEPRINT = { width: 560, height: 330 } as const

export const BLUEPRINT_VIEWBOX = `0 0 ${BLUEPRINT.width} ${BLUEPRINT.height}`

export const LABEL_X = 330

export const ROWS: readonly number[] = [52, 124, 196, 268]

export interface ProductArt {
  readonly strokes: readonly string[]
  readonly anchors: readonly (readonly [number, number])[]
}

export const ART: Readonly<Record<ProductKind, ProductArt>> = {
  phone: {
    strokes: [
      "M123 30H197A18 18 0 0 1 215 48V262A18 18 0 0 1 197 280H123A18 18 0 0 1 105 262V48A18 18 0 0 1 123 30Z",
      "M123 46H197A10 10 0 0 1 207 56V254A10 10 0 0 1 197 264H123A10 10 0 0 1 113 254V56A10 10 0 0 1 123 46Z",
      "M145 38H175",
      "M216 92V122",
      "M216 134V150",
      "M131 220H189M131 232H171",
    ],
    anchors: [
      [207, 100],
      [160, 150],
      [160, 226],
      [215, 250],
    ],
  },
  laptop: {
    strokes: [
      "M78 62H242A8 8 0 0 1 250 70V182H70V70A8 8 0 0 1 78 62Z",
      "M82 74H238V170H82Z",
      "M44 192H276L262 210H58Z",
      "M70 182H250",
      "M140 192V198H180V192",
    ],
    anchors: [
      [238, 100],
      [120, 150],
      [160, 196],
      [230, 200],
    ],
  },
  kettle: {
    strokes: [
      "M112 112Q160 92 208 112L224 258H96Z",
      "M124 108Q160 78 196 108",
      "M154 86A6 6 0 1 0 166 86A6 6 0 1 0 154 86",
      "M210 124Q262 132 254 192Q248 234 218 240",
      "M110 124L80 102L88 96",
      "M140 140H150V232H140Z",
      "M90 258H230V272H90Z",
    ],
    anchors: [
      [145, 160],
      [206, 140],
      [145, 226],
      [200, 266],
    ],
  },
  vacuum: {
    strokes: [
      "M160 70A95 95 0 1 1 159.9 70Z",
      "M160 86A79 79 0 1 1 159.9 86Z",
      "M160 92A18 18 0 1 1 159.9 92Z",
      "M74 128A95 95 0 0 1 246 128",
      "M150 165H170M160 155V175",
      "M88 222L70 240M80 214L62 220",
    ],
    anchors: [
      [160, 110],
      [160, 165],
      [222, 200],
      [100, 214],
    ],
  },
}

export function leaderPath(anchor: readonly [number, number], row: number): string {
  const [x, y] = anchor
  const knee = LABEL_X - 36
  return `M${x} ${y}L${knee} ${row}H${LABEL_X - 8}`
}
