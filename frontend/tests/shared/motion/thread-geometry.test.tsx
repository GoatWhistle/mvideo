import { afterEach, describe, expect, it } from "vitest"
import { measureThread, routePath } from "@/shared/motion/thread-layer/thread-geometry"

const METRICS = { lead: 12, rowAnchor: 22, radius: 10 }

function box(element: Element, left: number, top: number, width: number, height: number) {
  const rect = DOMRect.fromRect({ x: left, y: top, width, height })
  Object.assign(element, {
    getBoundingClientRect: () => rect,
    getClientRects: () => [rect],
  })
}

function board(textLeft: number, rowLeft: number) {
  document.body.innerHTML = `
    <div id="root">
      <section id="text" data-thread-lane><mark id="mark" data-thread-target="Color">black</mark></section>
      <section id="table" data-thread-lane><div id="row" data-thread-source="Color"></div></section>
    </div>`
  const at = (id: string) => document.getElementById(id) as HTMLElement
  box(at("root"), 0, 0, 1000, 800)
  box(at("text"), textLeft, 0, 400, 600)
  box(at("mark"), textLeft + 40, 100, 60, 20)
  box(at("table"), rowLeft, 0, 500, 800)
  box(at("row"), rowLeft + 20, 300, 460, 64)
  return at("root")
}

describe("measureThread", () => {
  afterEach(() => {
    document.body.innerHTML = ""
  })

  it("runs from the text lane edge at the quote line to the middle of the row", () => {
    const thread = measureThread(board(0, 448), "Color", METRICS)
    expect([thread?.startX, thread?.startY]).toEqual([400, 110])
    expect([thread?.endX, thread?.endY]).toEqual([448, 332])
    expect(thread?.path).toBe("M 400 110 H 414 Q 424 110 424 120 V 322 Q 424 332 434 332 H 448")
  })

  it("draws nothing when the lanes are stacked or the key is unknown", () => {
    expect(measureThread(board(0, 0), "Color", METRICS)).toBeNull()
    expect(measureThread(board(0, 448), "Brand", METRICS)).toBeNull()
  })

  it("points from a source panel on the right back to the selected row", () => {
    const thread = measureThread(board(548, 0), "Color", METRICS)
    expect([thread?.startX, thread?.endX]).toEqual([548, 500])
    expect(thread?.path).toBe("M 548 110 H 534 Q 524 110 524 120 V 322 Q 524 332 514 332 H 500")
  })
})

describe("routePath", () => {
  it("draws a level line without corners", () => {
    expect(routePath(0, 50, 40, 50, 10)).toBe("M 0 50 H 20 Q 20 50 20 50 V 50 Q 20 50 20 50 H 40")
  })

  it("shrinks the corners to fit a short rise", () => {
    expect(routePath(0, 0, 40, 6, 10)).toBe("M 0 0 H 17 Q 20 0 20 3 V 3 Q 20 6 23 6 H 40")
  })
})
