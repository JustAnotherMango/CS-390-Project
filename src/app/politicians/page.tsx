// app/politicians/page.tsx
"use client"

import React, { useState, useEffect, useMemo } from "react"
import Link from "next/link"
import { Card } from "@/components/ui/card"

type Trade = {
  politician: string
  party: string
  chamber: string
  state: string
  image: string
}

type PoliticianSummary = Trade

export default function PoliticiansList() {
  const [data, setData] = useState<PoliticianSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  // filter states
  const [searchTerm, setSearchTerm] = useState("")
  const [filterParty, setFilterParty] = useState("All")
  const [filterChamber, setFilterChamber] = useState("All")
  const [filterState, setFilterState] = useState("All")

  useEffect(() => {
    fetch("http://localhost:5000/Politicians")
      .then((res) => {
        if (!res.ok) throw new Error("Couldn’t load politicians")
        return res.json()
      })
      .then((json) => {
        // dedupe by politician name
        const map = new Map<string, PoliticianSummary>()
        ;(json.trades as Trade[]).forEach((t) => {
          if (!map.has(t.politician)) {
            map.set(t.politician, {
              politician: t.politician,
              party: t.party,
              chamber: t.chamber,
              state: t.state,
              image: t.image,
            })
          }
        })
        setData(Array.from(map.values()))
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  // derive unique filter options
  const parties = useMemo(
    () => ["All", ...new Set(data.map((t) => t.party))],
    [data]
  )
  const chambers = useMemo(
    () => ["All", ...new Set(data.map((t) => t.chamber))],
    [data]
  )
  const states = useMemo(
    () => ["All", ...new Set(data.map((t) => t.state))],
    [data]
  )

  // filtered list
  const filtered = useMemo(() => {
    return data.filter((t) => {
      if (filterParty !== "All" && t.party !== filterParty) return false
      if (filterChamber !== "All" && t.chamber !== filterChamber) return false
      if (filterState !== "All" && t.state !== filterState) return false
      if (
        searchTerm &&
        !t.politician.toLowerCase().includes(searchTerm.toLowerCase())
      )
        return false
      return true
    })
  }, [data, filterParty, filterChamber, filterState, searchTerm])

  if (loading) return <p className="text-center text-white mt-8">Loading…</p>
  if (error) return <p className="text-center text-red-500 mt-8">{error}</p>

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Search + Filters */}
      <div className="flex flex-col md:flex-row md:space-x-4 space-y-4 md:space-y-0 mb-6">
        <input
          type="text"
          placeholder="Search by name…"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 p-2 rounded bg-gray-800 text-white placeholder-gray-400"
        />
        <select
          value={filterParty}
          onChange={(e) => setFilterParty(e.target.value)}
          className="p-2 rounded bg-gray-800 text-white"
        >
          {parties.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <select
          value={filterChamber}
          onChange={(e) => setFilterChamber(e.target.value)}
          className="p-2 rounded bg-gray-800 text-white"
        >
          {chambers.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <select
          value={filterState}
          onChange={(e) => setFilterState(e.target.value)}
          className="p-2 rounded bg-gray-800 text-white"
        >
          {states.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {/* Cards */}
      <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 items-stretch">
        {filtered.map((p) => (
          <Link
            key={p.politician}
            href={`/politicians/${encodeURIComponent(p.politician)}`}
          >
            <Card
              className={`h-full p-4 cursor-pointer flex flex-row items-center space-x-4 ${
                p.party === "Democrat"
                  ? "bg-blue-800 text-white"
                  : p.party === "Republican"
                  ? "bg-red-800 text-white"
                  : "bg-gray-800 text-white"
              }`}
            >
              <div className="flex-1">
                <h3 className="text-xl font-semibold">{p.politician}</h3>
                <p className="text-sm">State: {p.state}</p>
                <p className="text-sm">Chamber: {p.chamber}</p>
              </div>
              <div className="flex-shrink-0">
                <img
                  src={p.image}
                  alt={p.politician}
                  className="w-20 h-20 rounded-full object-cover"
                />
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
