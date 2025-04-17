// app/politicians/[name]/page.tsx
"use client"

import React, { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card } from "@/components/ui/card"

type Trade = {
  id: number
  politician: string
  traded_issuer: string
  ticker: string
  trade_type: string
  min_purchase_price: number | null
  max_purchase_price: number | null
  trade_date: string
  published_date: string
  gap: string
}

export default function PoliticianDetail() {
  const { name } = useParams()
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!name) return
    fetch("http://localhost:5000/Politicians")
      .then(r => {
        if (!r.ok) throw new Error("Couldn’t load trades")
        return r.json()
      })
      .then(data => {
        const all: Trade[] = data.trades
        setTrades(all.filter(t => t.politician === name))
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [name])

  if (loading) return <p className="text-center text-white">Loading…</p>
  if (error)   return <p className="text-center text-red-500">{error}</p>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-white">{name}’s Trades</h1>
      <div className="grid gap-4">
        {trades.map(t => (
          <Card key={t.id} className="p-4 bg-gray-800 text-white">
            <p><strong>Issuer:</strong> {t.traded_issuer}</p>
            <p><strong>Ticker:</strong> {t.ticker}</p>
            <p><strong>Type:</strong> {t.trade_type}</p>
            <p>
              <strong>Size:</strong>{" "}
              {t.min_purchase_price ?? "N/A"}–{t.max_purchase_price ?? "N/A"}
            </p>
            <p><strong>Trade Date:</strong> {t.trade_date}</p>
            <p><strong>Published:</strong> {t.published_date}</p>
            <p><strong>Gap:</strong> {t.gap}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}
