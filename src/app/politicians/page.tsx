// app/politicians/page.tsx
"use client"

import React, { useState, useEffect } from "react"
import Link from "next/link"
import { Card } from "@/components/ui/card"

type Trade = {
  id: number
  politician: string
  party: string
  chamber: string
  state: string
}

type PoliticianSummary = {
  politician: string
  party: string
  chamber: string
  state: string
}

export default function PoliticiansList() {
  const [list, setList] = useState<PoliticianSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetch("http://localhost:5000/Politicians")
      .then((res) => {
        if (!res.ok) throw new Error("Couldn’t load politicians")
        return res.json()
      })
      .then((data) => {
        const map = new Map<string, PoliticianSummary>()
        ;(data.trades as Trade[]).forEach((t) => {
          if (!map.has(t.politician)) {
            map.set(t.politician, {
              politician: t.politician,
              party: t.party,
              chamber: t.chamber,
              state: t.state,
            })
          }
        })
        setList(Array.from(map.values()))
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-center text-white">Loading…</p>
  if (error) return <p className="text-center text-red-500">{error}</p>

  return (
    <div className="p-6 grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
      {list.map((p) => (
        <Link
          key={p.politician}
          href={`/politicians/${encodeURIComponent(p.politician)}`}
        >
          <Card
            className={`p-4 cursor-pointer ${
              p.party === "Democrat"
                ? "bg-blue-800 text-white"
                : p.party === "Republican"
                ? "bg-red-800 text-white"
                : "bg-gray-800 text-white"
            }`}
          >
            <h3 className="text-xl font-semibold">{p.politician}</h3>
            <p className="text-sm">State: {p.state}</p>
            <p className="text-sm">Chamber: {p.chamber}</p>
          </Card>
        </Link>
      ))}
    </div>
  )
}
