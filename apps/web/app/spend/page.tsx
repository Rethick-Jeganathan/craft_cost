"use client";
import * as React from 'react'

type Tx = {
  id: number
  user_id: number
  category: string | null
  merchant: string | null
  date: string | null
  amount: number | null
  description: string | null
}

export default function SpendPage() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
  const [summary, setSummary] = React.useState<{ period: string, total: number, by_category: Record<string, number> } | null>(null)
  const [items, setItems] = React.useState<Tx[]>([])
  const [cursor, setCursor] = React.useState<number | null>(null)
  const [loading, setLoading] = React.useState(false)

  React.useEffect(() => {
    fetch(`${apiBase}/v1/spend/summary?period=last_30d`).then(r => r.json()).then(setSummary).catch(() => {})
    loadMore()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function loadMore() {
    setLoading(true)
    try {
      const url = new URL(`${apiBase}/v1/transactions`)
      if (cursor) url.searchParams.set('cursor', String(cursor))
      url.searchParams.set('limit', '20')
      const res = await fetch(url.toString())
      const data = await res.json()
      setItems(prev => [...prev, ...data.items])
      setCursor(data.next_cursor)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-xl font-semibold text-white/90">Spend</h1>
        <p className="text-sm text-[var(--muted)]">Transactions and summary (read-only)</p>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-[var(--border)]/60 bg-[var(--surface)]/60 p-4">
          <div className="text-sm font-semibold text-white/90">Total (30d)</div>
          <div className="mt-2 text-2xl">${summary ? Math.abs(summary.total).toFixed(2) : '0.00'}</div>
        </div>
        <div className="sm:col-span-2 rounded-lg border border-[var(--border)]/60 bg-[var(--surface)]/60 p-4">
          <div className="text-sm font-semibold text-white/90">By Category</div>
          <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
            {summary && Object.entries(summary.by_category).map(([k, v]) => (
              <div key={k} className="flex items-center justify-between">
                <span className="text-[var(--muted)]">{k}</span>
                <span>${Math.abs(v).toFixed(2)}</span>
              </div>
            ))}
            {!summary && <div className="text-[var(--muted)]">No data</div>}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-[var(--border)]/60 bg-[var(--surface)]/60">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-[var(--muted)]">
              <tr>
                <th className="px-4 py-2">Date</th>
                <th className="px-4 py-2">Description</th>
                <th className="px-4 py-2">Merchant</th>
                <th className="px-4 py-2">Category</th>
                <th className="px-4 py-2 text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {items.map(tx => (
                <tr key={tx.id} className="border-t border-[var(--border)]/60">
                  <td className="px-4 py-2 whitespace-nowrap">{tx.date ?? ''}</td>
                  <td className="px-4 py-2">{tx.description ?? ''}</td>
                  <td className="px-4 py-2">{tx.merchant ?? ''}</td>
                  <td className="px-4 py-2">{tx.category ?? ''}</td>
                  <td className="px-4 py-2 text-right">{tx.amount != null ? `$${Math.abs(tx.amount).toFixed(2)}` : ''}</td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="px-4 py-6 text-center text-[var(--muted)]" colSpan={5}>No transactions yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="flex justify-center p-3">
          {cursor && (
            <button onClick={loadMore} disabled={loading} className="inline-flex items-center rounded-md border border-[var(--border)]/60 bg-transparent px-3 py-2 text-sm text-white hover:border-brand-600/50 disabled:opacity-50">
              {loading ? 'Loading...' : 'Load more'}
            </button>
          )}
        </div>
      </section>
    </div>
  )
}
