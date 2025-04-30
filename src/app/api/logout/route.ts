import { NextRequest, NextResponse } from "next/server"

export async function POST() {
  const res = await fetch("http://localhost:5000/logout", {
    method: "POST",
    credentials: "include",
  })

  const setCookie = res.headers.get("set-cookie")
  const data = await res.json()

  const nextRes = NextResponse.json(data, { status: res.status })
  if (setCookie) {
    nextRes.headers.set("set-cookie", setCookie)
  }
  return nextRes
}