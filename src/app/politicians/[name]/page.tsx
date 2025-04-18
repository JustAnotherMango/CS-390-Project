// app/politicians/[name]/page.tsx
"use client"

import React, { useState, useEffect, useMemo } from "react"
import { useParams } from "next/navigation"

type Trade = {
  id: number
  politician: string
  image: string
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
  const params = useParams()

  // normalize params.name to a single string before decoding
  const rawName = params.name
  const slug =
    typeof rawName === "string"
      ? rawName
      : Array.isArray(rawName)
      ? rawName[0]
      : ""
  const name = decodeURIComponent(slug)

  // data state
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  // filter inputs
  const [searchIssuer, setSearchIssuer] = useState("")
  const [filterType, setFilterType] = useState("All")
  const [filterTicker, setFilterTicker] = useState("All")

  // fetch on mount / name change
  useEffect(() => {
    if (!name) return
    fetch("http://localhost:5000/Politicians")
      .then((r) => {
        if (!r.ok) throw new Error("Couldn’t load trades")
        return r.json()
      })
      .then((json) => {
        const all: Trade[] = json.trades
        setTrades(all.filter((t) => t.politician === name))
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [name])

  // derive filter options
  const types = useMemo(
    () => ["All", ...new Set(trades.map((t) => t.trade_type))],
    [trades]
  )
  const tickers = useMemo(
    () => ["All", ...new Set(trades.map((t) => t.ticker))],
    [trades]
  )

  // apply filters + search
  const filtered = useMemo(
    () =>
      trades.filter((t) => {
        if (filterType !== "All" && t.trade_type !== filterType) return false
        if (filterTicker !== "All" && t.ticker !== filterTicker) return false
        if (
          searchIssuer &&
          !t.traded_issuer.toLowerCase().includes(searchIssuer.toLowerCase())
        )
          return false
        return true
      }),
    [trades, filterType, filterTicker, searchIssuer]
  )

  // early returns
  if (loading) {
    return <p className="text-center text-white mt-8">Loading…</p>
  }
  if (error) {
    return <p className="text-center text-red-500 mt-8">{error}</p>
  }
  if (trades.length === 0) {
    return (
      <p className="text-center text-white mt-8">
        No trades found for {name}
      </p>
    )
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header + image */}
      <div className="flex items-center space-x-4">
        {trades[0]?.image && (
          <img
            src={trades[0].image}
            alt={name}
            className="w-20 h-20 rounded-full object-cover"
          />
        )}
        <h1 className="text-3xl font-bold text-white">{name}’s Trades</h1>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row md:space-x-4 space-y-4 md:space-y-0">
        <input
          type="text"
          placeholder="Search issuer…"
          value={searchIssuer}
          onChange={(e) => setSearchIssuer(e.target.value)}
          className="flex-1 p-2 rounded bg-gray-800 text-white placeholder-gray-400"
        />
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="p-2 rounded bg-gray-800 text-white"
        >
          {types.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <select
          value={filterTicker}
          onChange={(e) => setFilterTicker(e.target.value)}
          className="p-2 rounded bg-gray-800 text-white"
        >
          {tickers.map((tk) => (
            <option key={tk} value={tk}>
              {tk}
            </option>
          ))}
        </select>
      </div>

      {/* Trades list */}
      <div className="space-y-4">
        {filtered.map((t) => (
          <div
            key={t.id}
            className="bg-gray-800 text-white p-4 rounded-lg grid 
                       grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 items-center"
          >
            <div className="font-medium">{t.traded_issuer}</div>
            <div>{t.ticker}</div>
            <div>{t.trade_type}</div>
            <div>
              {t.min_purchase_price ?? "N/A"}–{t.max_purchase_price ?? "N/A"}
            </div>
            <div>{t.trade_date}</div>
            <div>{t.published_date}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
