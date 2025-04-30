import { NextRequest, NextResponse } from "next/server"

export async function GET(req: NextRequest) {
  const cookie = req.headers.get("cookie") || ""

  const res = await fetch("http://localhost:5000/me", {
    method: "GET",
    headers: {
      cookie,
    },
    credentials: "include",
  })

  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}