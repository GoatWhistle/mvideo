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
      "M80 60H240A8 8 0 0 1 248 68V190H72V68A8 8 0 0 1 80 60Z",
      "M84 72H236V180H84Z",
      "M52 190H268L256 206H64Z",
      "M138 190Q160 198 182 190",
      "M158 66H162",
    ],
    anchors: [
      [236, 100],
      [130, 150],
      [244, 200],
      [92, 200],
    ],
  },
  kettle: {
    strokes: [
      "M104 258L116 120Q160 108 204 120L216 258Z",
      "M116 120Q160 96 204 120",
      "M155 108V100H165V108",
      "M116 132L86 116L90 110L117 122",
      "M204 128Q248 128 248 170V214Q248 240 214 242",
      "M140 150H150V236H140Z",
      "M140 196H150",
      "M96 258H224V270H96Z",
    ],
    anchors: [
      [190, 136],
      [145, 196],
      [145, 228],
      [200, 264],
    ],
  },
  vacuum: {
    strokes: [
      "M160 75A95 95 0 0 1 160 265A95 95 0 0 1 160 75Z",
      "M84.7 126.5A87 87 0 0 1 235.3 126.5",
      "M160 104A16 16 0 0 1 160 136A16 16 0 0 1 160 104Z",
      "M160 182A8 8 0 0 1 160 198A8 8 0 0 1 160 182Z",
      "M98 214A10 10 0 0 1 98 234A10 10 0 0 1 98 214Z",
      "M98 214L94 202M106 230L118 236M90 230L80 238",
      "M120 246Q160 258 200 246",
    ],
    anchors: [
      [160, 120],
      [160, 190],
      [222, 208],
      [160, 251],
    ],
  },
}

export function leaderPath(anchor: readonly [number, number], row: number): string {
  const [x, y] = anchor
  const knee = LABEL_X - 36
  return `M${x} ${y}L${knee} ${row}H${LABEL_X - 8}`
}
