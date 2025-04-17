// app/layout.tsx
import React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import Link from "next/link"
import "./globals.css"

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] })
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Politrade2",
  description: "next up and coming political trading app",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-900`}
      >
        <header className="sticky top-0 bg-gray-950 border-b border-gray-800 p-4">
          <nav>
            <ul className="flex space-x-6">
              <li>
                <Link href="/" className="text-white hover:text-green-600">
                  Home
                </Link>
              </li>
              <li>
                <Link
                  href="/politicians"
                  className="text-white hover:text-green-600"
                >
                  Politicians
                </Link>
              </li>
              {/* add other links here */}
            </ul>
          </nav>
        </header>

        <main>{children}</main>
      </body>
    </html>
  )
}
