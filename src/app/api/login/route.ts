import { NextRequest, NextResponse } from "next/server"

export async function POST(req: NextRequest) {
  const body = await req.json()

  const res = await fetch("http://localhost:5000/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
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