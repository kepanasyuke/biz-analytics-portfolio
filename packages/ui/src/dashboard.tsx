import type { Block, Dashboard, Kpi, Series, TableBlock } from './types'
import { BarChart, Donut, Funnel, Heatmap, LineChart } from './charts'
import { Card, DataTable, ErrorBox, Section, Spinner } from './components'
import { useResource, type Resource } from './hooks/useResource'

export type Theme = { accent?: string; mark?: string }

const themeStyle = (theme: Theme): Record<string, string> => ({ '--blue': theme.accent ?? '#0060ff' })

const Chevron = ({ tone = 'light', size = 20 }: { tone?: 'light' | 'dark'; size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M4 15.5 L12 7 L20 15.5"
      fill="none"
      stroke={tone === 'light' ? '#ffffff' : 'var(--blue)'}
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

const TopBar = ({ brand, period, updated }: { brand: string; period: string; updated: string }) => (
  <div className="wrap">
    <header className="topbar">
      <div className="brand">
        <Chevron tone="dark" size={22} />
        <span>{brand}</span>
      </div>
      <div className="topbar__meta">
        {period}
        <br />
        обновлено {updated}
      </div>
    </header>
  </div>
)

const Statement = ({ kpi, index }: { kpi: Kpi; index: number }) => (
  <div className="statement">
    <span className="statement__index">{index}</span>
    <span className="statement__label">{kpi.label}</span>
    <span className="statement__value">{kpi.value}</span>
    {kpi.hint ? <span className="statement__hint">{kpi.hint}</span> : null}
  </div>
)

const Chip = ({ kpi }: { kpi: Kpi }) => (
  <div className="chip">
    <span className="chip__label">{kpi.label}</span>
    <span className="chip__value">{kpi.value}</span>
  </div>
)

const Hero = ({ meta, kpis }: { meta: Dashboard['meta']; kpis: Kpi[] }) => (
  <section className="hero">
    <div className="wrap">
      <div className="hero__eyebrow">
        <Chevron tone="light" size={14} />
        <span>Аналитика</span>
        <span>·</span>
        <span>{meta.source}</span>
      </div>
      <h1 className="hero__title">{meta.title}</h1>
      <p className="hero__lead">{meta.subtitle}</p>
      <div className="statements">
        {kpis.slice(0, 3).map((kpi, index) => (
          <Statement key={kpi.label} kpi={kpi} index={index + 1} />
        ))}
      </div>
      <div className="chips">
        {kpis.slice(3).map((kpi) => (
          <Chip key={kpi.label} kpi={kpi} />
        ))}
      </div>
    </div>
  </section>
)

const SeriesCard = ({ series, span }: { series: Series; span: 4 | 6 | 8 | 12 }) => (
  <Card title={series.title} note={series.unit} span={span}>
    {series.kind === 'line' ? <LineChart points={series.points} /> : <BarChart points={series.points} />}
  </Card>
)

const BlockView = ({ block }: { block: Block }) => (
  <Card title={block.title} note={block.note} span={6}>
    {block.kind === 'funnel' ? <Funnel points={block.points} /> : null}
    {block.kind === 'donut' ? <Donut points={block.points} /> : null}
    {block.kind === 'bars' ? <BarChart points={block.points} /> : null}
    {block.kind === 'heatmap' ? <Heatmap columns={block.columns} rows={block.rows} /> : null}
  </Card>
)

const TableCard = ({ table }: { table: TableBlock }) => (
  <Card title={table.title} note={table.note} span={12}>
    <DataTable columns={table.columns} rows={table.rows} />
  </Card>
)

const SeriesGrid = ({ series }: { series: Series[] }) => (
  <>
    <Section index={1} title="Динамика" note="Факт по месяцам, сглаженных значений нет — только исходные данные" />
    <div className="grid">
      {series.map((item, index) => (
        <SeriesCard key={item.key} series={item} span={index === 0 ? 12 : 6} />
      ))}
    </div>
  </>
)

const BlockGrid = ({ blocks }: { blocks: Block[] }) => (
  <>
    <Section index={2} title="Структура и разрезы" note="Срезы построены SQL-запросами по сырым транзакциям" />
    <div className="grid">{blocks.map((block) => <BlockView key={block.title} block={block} />)}</div>
  </>
)

const TableGrid = ({ tables }: { tables: TableBlock[] }) => (
  <>
    <Section index={3} title="Детализация" note="Полные таблицы доступны через /api/dashboard" />
    <div className="grid">{tables.map((table) => <TableCard key={table.title} table={table} />)}</div>
  </>
)

const Ready = ({ data, theme }: { data: Dashboard; theme: Theme }) => (
  <div className="page" style={themeStyle(theme)}>
    <TopBar brand={data.meta.brand} period={data.meta.period} updated={data.meta.updated} />
    <Hero meta={data.meta} kpis={data.kpis} />
    <main className="wrap main">
      <SeriesGrid series={data.series} />
      <BlockGrid blocks={data.blocks} />
      <TableGrid tables={data.tables} />
    </main>
    <div className="wrap">
      <footer className="footer">
        <span>
          {data.meta.brand} · {data.meta.source}
        </span>
        <span>{data.meta.subtitle}</span>
      </footer>
    </div>
  </div>
)

export function DashboardApp({ theme = {}, endpoint = '/api/dashboard' }: { theme?: Theme; endpoint?: string }) {
  const state = useResource<Dashboard>(endpoint)
  return renderState(state, theme)
}

const renderState = (state: Resource<Dashboard>, theme: Theme) =>
  state.error ? <ErrorBox message={state.error} /> : state.data ? <Ready data={state.data} theme={theme} /> : <Spinner />

export const DashboardShell = { DashboardApp, Ready }
