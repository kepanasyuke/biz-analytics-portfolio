import type { HeatRow, Point } from './types'
import { compact } from './format'

export type Size = { width: number; height: number }
export type Pt = { x: number; y: number }

const DEFAULT_SIZE: Size = { width: 720, height: 200 }
const RADIUS = 54
const STROKE = 16
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const PALETTE = ['#0060ff', '#4d8bff', '#9dbcff', '#0043b8', '#c9d8f5', '#0a0a0a']

export const totalOf = (points: Point[]): number => points.reduce((sum, point) => sum + point.value, 0)

export const sumOf = (points: Point[]): number => totalOf(points)

export const maxOf = (values: number[]): number => Math.max(1, ...values)

export const share = (value: number, total: number): number => (total === 0 ? 0 : value / total)

const round = (value: number): number => Math.round(value * 10) / 10

const pointAt = (value: number, index: number, count: number, max: number, size: Size): Pt => ({
  x: round((index / Math.max(1, count - 1)) * size.width),
  y: round(size.height - share(value, max) * size.height),
})

const maxValueOf = (points: Point[]): number => maxOf(points.map((point) => point.value))

const mapPoints = (points: Point[], size: Size): Pt[] =>
  points.map((point, index) => pointAt(point.value, index, points.length, maxValueOf(points), size))

export const pathOf = (points: Pt[]): string =>
  points.map((point, index) => `${index === 0 ? 'M' : 'L'}${point.x},${point.y}`).join(' ')

const areaOf = (points: Pt[], height: number): string => `${pathOf(points)} L ${points.at(-1)?.x ?? 0},${height} L 0,${height} Z`

const plotOf = (points: Point[], size: Size): { points: Pt[]; width: number; height: number } => ({
  points: mapPoints(points, size),
  width: size.width,
  height: size.height,
})

const step = (points: Point[]): number => Math.max(1, Math.ceil(points.length / 7))

const labelsOf = (points: Point[]): JSX.Element[] =>
  points.filter((_, index) => index % step(points) === 0 || index === points.length - 1).map((point) => (
    <span key={point.label}>{point.label}</span>
  ))

export function LineChart({ points, size = DEFAULT_SIZE }: { points: Point[]; size?: Size }) {
  const plot = plotOf(points, size)
  return (
    <figure className="chart">
      <svg viewBox={`0 0 ${plot.width} ${plot.height}`} role="img">
        <path className="chart__area" d={areaOf(plot.points, plot.height)} />
        <path className="chart__line" d={pathOf(plot.points)} />
        {plot.points.map((point, index) => (
          <circle key={index} className="chart__dot" cx={point.x} cy={point.y} r={3} />
        ))}
      </svg>
      <div className="chart__axis">{labelsOf(points)}</div>
    </figure>
  )
}

function BarRow({ point, max, format }: { point: Point; max: number; format: (value: number) => string }) {
  const width = Math.max(2, Math.round(share(point.value, max) * 100))
  return (
    <div className="bars__row">
      <span className="bars__label" title={point.label}>
        {point.label}
      </span>
      <div className="bars__track">
        <div className="bars__fill" style={{ width: `${width}%` }} />
      </div>
      <span className="bars__value">{format(point.value)}</span>
    </div>
  )
}

export function BarChart({ points, format = compact }: { points: Point[]; format?: (value: number) => string }) {
  const max = maxValueOf(points)
  return <div className="bars">{points.map((point) => <BarRow key={point.label} point={point} max={max} format={format} />)}</div>
}

const arcOf = (value: number, total: number, offset: number): { dash: string; shift: string } => ({
  dash: `${(share(value, total) * CIRCUMFERENCE).toFixed(2)} ${CIRCUMFERENCE.toFixed(2)}`,
  shift: (-offset * CIRCUMFERENCE).toFixed(2),
})

const arcsOf = (points: Point[]): { dash: string; shift: string }[] =>
  points.map((point, index) => arcOf(point.value, totalOf(points), sumOf(points.slice(0, index))))

const LegendRow = ({ point, total, color }: { point: Point; total: number; color: string }) => (
  <div className="legend__row">
    <span className="legend__dot" style={{ background: color }} />
    <span>{point.label}</span>
    <span className="legend__value">
      {compact(point.value)} · {Math.round(share(point.value, total) * 100)}%
    </span>
  </div>
)

export const Legend = ({ points, total }: { points: Point[]; total: number }) => (
  <div className="legend">
    {points.map((point, index) => (
      <LegendRow key={point.label} point={point} total={total} color={PALETTE[index % PALETTE.length] ?? '#0060ff'} />
    ))}
  </div>
)

export function Donut({ points, caption = 'всего' }: { points: Point[]; caption?: string }) {
  const arcs = arcsOf(points)
  return (
    <div className="donut">
      <svg viewBox="0 0 140 140" role="img">
        <circle cx="70" cy="70" r={RADIUS} fill="none" stroke="var(--line-soft)" strokeWidth={STROKE} />
        {arcs.map((arc, index) => (
          <circle
            key={index}
            cx="70"
            cy="70"
            r={RADIUS}
            fill="none"
            stroke={PALETTE[index % PALETTE.length] ?? '#0060ff'}
            strokeWidth={STROKE}
            strokeDasharray={arc.dash}
            strokeDashoffset={arc.shift}
            transform="rotate(-90 70 70)"
          />
        ))}
        <text x="70" y="68" textAnchor="middle" className="donut__value">
          {compact(totalOf(points))}
        </text>
        <text x="70" y="84" textAnchor="middle" className="donut__center">
          {caption}
        </text>
      </svg>
      <Legend points={points} total={totalOf(points)} />
    </div>
  )
}

const previousOf = (points: Point[], index: number): number => points[index - 1]?.value ?? points[index]?.value ?? 1

function FunnelStep({ point, width, rate, tint }: { point: Point; width: number; rate: number; tint: boolean }) {
  const style = { width: `${Math.max(12, Math.round(width * 100))}%` }
  return (
    <div className="funnel__step">
      <span className="funnel__label">{point.label}</span>
      <div className={`funnel__bar${tint ? ' funnel__bar--fade' : ''}`} style={style}>
        {compact(point.value)}
      </div>
      <span className="funnel__rate">{tint ? '—' : `${Math.round(rate * 100)}%`}</span>
    </div>
  )
}

export function Funnel({ points }: { points: Point[] }) {
  const first = points[0]?.value ?? 1
  return (
    <div className="funnel">
      {points.map((point, index) => (
        <FunnelStep
          key={point.label}
          point={point}
          width={share(point.value, first)}
          rate={share(point.value, previousOf(points, index))}
          tint={index === 0}
        />
      ))}
    </div>
  )
}

const cellStyle = (value: number, max: number): { background: string; color: string } => {
  const alpha = 0.08 + 0.78 * share(value, max)
  return { background: `rgba(0, 96, 255, ${alpha.toFixed(2)})`, color: alpha > 0.55 ? '#fff' : 'var(--ink)' }
}

export function Heatmap({ columns, rows }: { columns: string[]; rows: HeatRow[] }) {
  const max = maxValueOf(rows.flatMap((row) => row.cells.map((value) => ({ label: row.label, value }))))
  return (
    <div className="heatmap">
      {rows.map((row) => (
        <div key={row.label} className="heatmap__row" style={{ ['--cells' as string]: columns.length }}>
          <span className="bars__label">{row.label}</span>
          {row.cells.map((value, index) => (
            <span key={index} className="heatmap__cell" style={cellStyle(value, max)}>
              {Math.round(value)}
            </span>
          ))}
        </div>
      ))}
      <div className="heatmap__row">
        <span />
        {columns.map((column) => (
          <span key={column} className="chart__axis" style={{ justifyContent: 'center', fontSize: 11 }}>
            {column}
          </span>
        ))}
      </div>
    </div>
  )
}
