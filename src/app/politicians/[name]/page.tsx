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

  // filter inputs
  const [searchIssuer, setSearchIssuer] = useState("")
  const [filterType, setFilterType] = useState("All")
  const [filterTicker, setFilterTicker] = useState("All")
  // sort input
  const [sortOption, setSortOption] = useState("dateDesc")

  // helper: format numbers to k/m
  const formatAmount = (val: number | null): string => {
    if (val == null) return "N/A"
    if (val >= 1_000_000) {
      const m = val / 1_000_000
      return (Number.isInteger(m) ? m : +m.toFixed(1)) + "m"
    }
    if (val >= 1_000) {
      const k = val / 1_000
      return (Number.isInteger(k) ? k : +k.toFixed(1)) + "k"
    }
    return val.toString()
  }

  // fetch + normalize data
  useEffect(() => {
    if (!name) return
    fetch("http://localhost:5000/Politicians")
      .then((r) => {
        if (!r.ok) throw new Error("Couldn’t load trades")
        return r.json()
      })
      .then((json) => {
        const all: Trade[] = (json.trades as any[])
          .map((t) => ({
            ...t,
            min_purchase_price: t.min_purchase_price ? Number(t.min_purchase_price) : null,
            max_purchase_price: t.max_purchase_price ? Number(t.max_purchase_price) : null,
            avg_roi: t.avg_roi != null ? Number(t.avg_roi) : null,
          }))
          .filter((t) => t.politician === name)
        setTrades(all)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [name])

  // derive filter options
  const types = useMemo(
    () => ["All", ...Array.from(new Set(trades.map((t) => t.trade_type)))],
    [trades]
  )
  const tickers = useMemo(
    () => ["All", ...Array.from(new Set(trades.map((t) => t.ticker)))],
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
          !t.traded_issuer
            .split("\n")[0]
            .toLowerCase()
            .includes(searchIssuer.toLowerCase())
        )
          return false
        return true
      }),
    [trades, filterType, filterTicker, searchIssuer]
  )

  // sort filtered list
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
        return arr.sort((a, b) => {
          const sa = ((a.min_purchase_price ?? 0) + (a.max_purchase_price ?? 0)) / 2
          const sb = ((b.min_purchase_price ?? 0) + (b.max_purchase_price ?? 0)) / 2
          return sa - sb
        })
      case "sizeDesc":
        return arr.sort((a, b) => {
          const sa = ((a.min_purchase_price ?? 0) + (a.max_purchase_price ?? 0)) / 2
          const sb = ((b.min_purchase_price ?? 0) + (b.max_purchase_price ?? 0)) / 2
          return sb - sa
        })
      default:
        return arr
    }
  }, [filtered, sortOption])

  if (loading) return <p className="text-center text-white mt-8">Loading…</p>
  if (error) return <p className="text-center text-red-500 mt-8">{error}</p>
  if (!trades.length)
    return (
      <p className="text-center text-white mt-8">
        No trades found for {name}
      </p>
    )

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

      {/* Filters + Sort */}
      <div className="grid grid-cols-7 gap-4 mb-4">
        {/* Search issuer (now 3/7 width) */}
        <div className="col-span-3">
          <input
            type="text"
            placeholder="Search issuer…"
            value={searchIssuer}
            onChange={(e) => setSearchIssuer(e.target.value)}
            className="w-full p-2 rounded bg-gray-800 text-white placeholder-gray-400"
          />
        </div>
        {/* Trade type */}
        <div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="w-full p-2 rounded bg-gray-800 text-white"
          >
            {types.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        {/* Ticker */}
        <div>
          <select
            value={filterTicker}
            onChange={(e) => setFilterTicker(e.target.value)}
            className="w-full p-2 rounded bg-gray-800 text-white"
          >
            {tickers.map((tk) => (
              <option key={tk} value={tk}>
                {tk}
              </option>
            ))}
          </select>
        </div>
        {/* Sort options (2/7 width) */}
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

      {/* Column Headers */}
      <div className="bg-gray-700 text-gray-300 p-2 rounded-lg grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 font-semibold">
        <div>Issuer</div>
        <div>Ticker</div>
        <div>Type</div>
        <div>Size</div>
        <div>Trade Date</div>
        <div>Published</div>
        <div>Avg ROI</div>
      </div>

      {/* Trades list */}
      <div className="space-y-4">
        {sortedTrades.map((t) => (
          <div
            key={t.id}
            className="bg-gray-800 text-white p-4 rounded-lg grid 
                       grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 items-center"
          >
            <div className="font-medium">
              {t.traded_issuer.split("\n")[0]}
            </div>
            <div>{t.ticker}</div>
            <div>{t.trade_type}</div>
            <div>
              {formatAmount(t.min_purchase_price)} –{" "}
              {formatAmount(t.max_purchase_price)}
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
