import type { CSSProperties } from "react"
import { useCycle } from "../../../motion"
import {
  ART,
  BLUEPRINT_VIEWBOX,
  LABEL_X,
  leaderPath,
  type ProductKind,
  ROWS,
} from "./blueprint-art"
import styles from "./spec-blueprint.module.css"

export interface BlueprintCallout {
  readonly label: string
  readonly value: string
  readonly quote: string
}

export interface BlueprintProduct {
  readonly kind: ProductKind
  readonly name: string
  readonly callouts: readonly BlueprintCallout[]
}

export interface SpecBlueprintProps {
  readonly products: readonly BlueprintProduct[]
}

const GRID = [40, 100, 160, 220, 280]

function order(index: number): CSSProperties {
  return { "--i": index } as CSSProperties
}

export function SpecBlueprint({ products }: SpecBlueprintProps) {
  const active = useCycle(products.length, 3)
  const product = products[active]
  if (product === undefined) return null
  const art = ART[product.kind]
  return (
    <figure className={styles.figure} data-card-flow>
      <svg
        className={styles.scene}
        viewBox={BLUEPRINT_VIEWBOX}
        aria-hidden="true"
        focusable="false"
      >
        <g className={styles.grid}>
          {GRID.map((y) => (
            <path key={`h${y}`} d={`M0 ${y}H300`} />
          ))}
          {GRID.map((x) => (
            <path key={`v${x}`} d={`M${x} 0V310`} />
          ))}
        </g>
        <g key={product.kind}>
          {art.strokes.map((d, index) => (
            <path
              key={d}
              className={styles.stroke}
              d={d}
              pathLength={1}
              style={order(index)}
              data-signal
            />
          ))}
          {product.callouts.slice(0, ROWS.length).map((callout, index) => {
            const anchor = art.anchors[index]
            const row = ROWS[index]
            if (anchor === undefined || row === undefined) return null
            return (
              <g key={callout.label} className={styles.callout} style={order(index)}>
                <path className={styles.leader} d={leaderPath(anchor, row)} pathLength={1} />
                <circle className={styles.ping} cx={anchor[0]} cy={anchor[1]} r={4} />
                <circle className={styles.anchor} cx={anchor[0]} cy={anchor[1]} r={3.5} />
                <text className={styles.label} x={LABEL_X} y={row - 10}>
                  {callout.label}
                </text>
                <text className={styles.value} x={LABEL_X} y={row + 9}>
                  {callout.value}
                </text>
                <text className={styles.quote} x={LABEL_X} y={row + 27}>
                  {callout.quote}
                </text>
              </g>
            )
          })}
        </g>
      </svg>
      <figcaption className={styles.tabs}>
        {products.map((item, index) => (
          <span key={item.kind} className={styles.tab} data-active={index === active}>
            {item.name}
          </span>
        ))}
      </figcaption>
    </figure>
  )
}
