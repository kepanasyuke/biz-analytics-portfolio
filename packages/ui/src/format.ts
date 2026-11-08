import type { Column, ColumnKind, Row } from './types'

const numberFormat = new Intl.NumberFormat('ru-RU')
const compactFormat = new Intl.NumberFormat('ru-RU', { notation: 'compact', maximumFractionDigits: 1 })
const MONTH_NAMES = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']

export const compact = (value: number): string => compactFormat.format(value)

export const int = (value: number): string => numberFormat.format(Math.round(value))

export const money = (value: number): string => `${numberFormat.format(Math.round(value))} ₽`

export const compactMoney = (value: number): string => `${compactFormat.format(value)} ₽`

export const pct = (value: number): string => `${value.toFixed(1).replace('.', ',')}%`

export const ratio = (value: number): string => value.toFixed(2).replace('.', ',')

export const signedPct = (value: number): string => `${value > 0 ? '+' : ''}${pct(value)}`

const FORMATTERS: Record<ColumnKind, (value: number) => string> = {
  text: (value: number) => String(value),
  money: money,
  int: int,
  pct: pct,
  ratio: ratio,
}

export const renderCell = (row: Row, column: Column): string => {
  const value = row[column.key]
  return typeof value === 'number' ? FORMATTERS[column.kind ?? 'text'](value) : String(value ?? '—')
}

export const humanPeriod = (iso: string): string => {
  const [year, month] = iso.split('-')
  return `${MONTH_NAMES[Number(month) - 1] ?? '??'} ${year ?? ''}`
}
