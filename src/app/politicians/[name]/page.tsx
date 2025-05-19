// app/politicians/[name]/page.tsx
"use client"

import React, { useState, useEffect, useMemo } from "react"
import { useParams } from "next/navigation"

type Trade = {
  id: number
  politician: string
  image: string | null
  traded_issuer: string
  ticker: string
  trade_type: string
  min_purchase_price: number | null
  max_purchase_price: number | null
  trade_date: string
  published_date: string
  gap: string
  avg_roi: number | null
}

export default function PoliticianDetail() {
  const params = useParams()
  const rawName = params.name
  const name =
    typeof rawName === "string"
      ? decodeURIComponent(rawName)
      : Array.isArray(rawName) && rawName.length > 0
      ? decodeURIComponent(rawName[0])
      : ""

  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  // filters & sort
  const [searchIssuer, setSearchIssuer] = useState("")
  const [filterType, setFilterType] = useState("All")
  const [filterTicker, setFilterTicker] = useState("All")
  const [sortOption, setSortOption] = useState("dateDesc")

  useEffect(() => {
    if (!name) return
    fetch("http://localhost:5000/Trades")
      .then((res) => {
        if (!res.ok) throw new Error("Couldn’t load trades")
        return res.json()
      })
      .then((json: any[]) => {
        const all = (json as any[])
          .filter((t) => t.politician === name)
          .map((t) => ({
            id:                   t.id,
            politician:          t.politician,
            image:               t.image ?? null,
            traded_issuer:       t.traded_issuer || "",
            ticker:              t.ticker || "",
            trade_type:          t.trade_type || "",
            min_purchase_price:  t.min_purchase_price != null ? Number(t.min_purchase_price) : null,
            max_purchase_price:  t.max_purchase_price != null ? Number(t.max_purchase_price) : null,
            trade_date:          t.trade_date,
            published_date:      t.published_date,
            gap:                 t.gap || "",
            avg_roi:             t.avg_roi != null ? Number(t.avg_roi) : null,
          }))
        setTrades(all)
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

  // apply filters
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

  // apply sorting
  const sortedTrades = useMemo(() => {
    const arr = [...filtered]
    switch (sortOption) {
      case "dateAsc":
        return arr.sort(
          (a, b) =>
            new Date(a.trade_date).getTime() - new Date(b.trade_date).getTime()
        )
      case "dateDesc":
        return arr.sort(
          (a, b) =>
            new Date(b.trade_date).getTime() - new Date(a.trade_date).getTime()
        )
      case "sizeAsc":
        return arr.sort(
          (a, b) =>
            ((a.min_purchase_price ?? 0) + (a.max_purchase_price ?? 0)) / 2 -
            ((b.min_purchase_price ?? 0) + (b.max_purchase_price ?? 0)) / 2
        )
      case "sizeDesc":
        return arr.sort(
          (a, b) =>
            ((b.min_purchase_price ?? 0) + (b.max_purchase_price ?? 0)) / 2 -
            ((a.min_purchase_price ?? 0) + (a.max_purchase_price ?? 0)) / 2
        )
      default:
        return arr
    }
  }, [filtered, sortOption])

  if (loading) return <p className="text-center text-white mt-8">Loading…</p>
  if (error)   return <p className="text-center text-red-500 mt-8">{error}</p>
  if (!trades.length)
    return <p className="text-center text-white mt-8">No trades found for {name}</p>

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Filters & Sort */}
      <div className="grid grid-cols-7 gap-4 mb-4">
        <div className="col-span-3">
          <input
            type="text"
            placeholder="Search issuer…"
            value={searchIssuer}
            onChange={(e) => setSearchIssuer(e.target.value)}
            className="w-full p-2 rounded bg-gray-800 text-white placeholder-gray-400"
          />
        </div>
        <div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="w-full p-2 rounded bg-gray-800 text-white"
          >
            {types.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <select
            value={filterTicker}
            onChange={(e) => setFilterTicker(e.target.value)}
            className="w-full p-2 rounded bg-gray-800 text-white"
          >
            {tickers.map((tk) => (
              <option key={tk} value={tk}>{tk}</option>
            ))}
          </select>
        </div>
        <div className="col-span-2">
          <select
            value={sortOption}
            onChange={(e) => setSortOption(e.target.value)}
            className="w-full p-2 rounded bg-gray-800 text-white"
          >
            <option value="dateDesc">Date: newest → oldest</option>
            <option value="dateAsc">Date: oldest → newest</option>
            <option value="sizeDesc">Size: large → small</option>
            <option value="sizeAsc">Size: small → large</option>
          </select>
        </div>
      </div>

      {/* Trades Table */}
      <div className="bg-gray-700 text-gray-300 p-2 rounded-lg grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 font-semibold">
        <div>Issuer</div>
        <div>Ticker</div>
        <div>Type</div>
        <div>Size</div>
        <div>Trade Date</div>
        <div>Published</div>
        <div>Avg ROI</div>
      </div>
      <div className="space-y-4">
        {sortedTrades.map((t) => (
          <div
            key={t.id}
            className="bg-gray-800 text-white p-4 rounded-lg grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 items-center"
          >
            <div className="font-medium">{t.traded_issuer}</div>
            <div>{t.ticker}</div>
            <div>{t.trade_type}</div>
            <div>
              {(t.min_purchase_price ?? 0).toLocaleString()} –{" "}
              {(t.max_purchase_price ?? 0).toLocaleString()}
            </div>
            <div>{t.trade_date}</div>
            <div>{t.published_date}</div>
            <div>
              {t.avg_roi != null ? `${t.avg_roi.toFixed(2)}%` : "N/A"}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
