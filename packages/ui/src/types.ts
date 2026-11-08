export type Point = { label: string; value: number }

export type KpiTone = 'up' | 'down' | 'flat'

export type Kpi = { label: string; value: string; hint?: string; delta?: number; tone?: KpiTone }

export type Series = { key: string; title: string; kind: 'line' | 'bar'; unit?: string; points: Point[] }

export type ColumnKind = 'text' | 'money' | 'int' | 'pct' | 'ratio'

export type Column = { key: string; title: string; kind?: ColumnKind; align?: 'left' | 'right' }

export type Row = Record<string, string | number | null>

export type TableBlock = { title: string; note?: string; columns: Column[]; rows: Row[] }

export type HeatRow = { label: string; cells: number[] }

export type Block =
  | { kind: 'funnel'; title: string; note?: string; points: Point[] }
  | { kind: 'donut'; title: string; note?: string; points: Point[] }
  | { kind: 'bars'; title: string; note?: string; points: Point[] }
  | { kind: 'heatmap'; title: string; note?: string; columns: string[]; rows: HeatRow[] }

export type Meta = {
  brand: string
  title: string
  subtitle: string
  period: string
  updated: string
  source: string
}

export type Dashboard = {
  meta: Meta
  kpis: Kpi[]
  series: Series[]
  blocks: Block[]
  tables: TableBlock[]
}
