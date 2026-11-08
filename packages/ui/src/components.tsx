import type { ReactNode } from 'react'
import type { Column, Row } from './types'
import { renderCell } from './format'

export const Badge = ({ tone, children }: { tone: 'up' | 'down' | 'flat'; children: ReactNode }) => (
  <span className={`badge badge--${tone}`}>{children}</span>
)

export const Section = ({ index, title, note }: { index: number; title: string; note?: string }) => (
  <div className="section">
    <h2 className="section__title">
      <span className="section__index">{index}</span>
      {title}
    </h2>
    {note ? <p className="section__note">{note}</p> : null}
  </div>
)

export const Card = ({ title, note, children, span = 4, tint }: { title: string; note?: string; children: ReactNode; span?: 4 | 6 | 8 | 12; tint?: boolean }) => (
  <section className={`card col-${span}${tint ? ' card--tint' : ''}`}>
    <header className="card__head">
      <h3 className="card__title">{title}</h3>
      {note ? <span className="card__note">{note}</span> : null}
    </header>
    {children}
  </section>
)

export const DataTable = ({ columns, rows }: { columns: Column[]; rows: Row[] }) => (
  <div className="table-wrap">
    <table className="data">
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={column.key} className={column.align === 'right' ? 'num' : ''}>
              {column.title}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={index}>
            {columns.map((column) => (
              <td key={column.key} className={column.align === 'right' ? 'num' : ''}>
                {renderCell(row, column)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)

export const Spinner = ({ label = 'Считаю данные…' }: { label?: string }) => <div className="state">{label}</div>

export const ErrorBox = ({ message }: { message: string }) => (
  <div className="state">
    <div className="state__error">Не удалось получить данные</div>
    <div>{message}</div>
  </div>
)
