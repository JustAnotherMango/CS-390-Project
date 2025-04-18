// app/layout.tsx
import React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import Link from "next/link"
import "./globals.css"

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] })
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Politrade",
  description: "Next up and coming political trading app",
}



export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-900`}>
        <header className="sticky top-0 border-b-2 border-green-600 bg-gray-950 p-5 text-white z-10">
          <nav className="flex justify-between items-center max-w-screen mx-auto">
            <Link href="/" className="text-2xl font-semibold font-serif">
              Politrade
            </Link>
            <ul className="flex space-x-8">
              <li>
                <Link href="/politicians" className="hover:text-green-600">
                  Politicians
                </Link>
              </li>
              <li>
                <a href="#about" className="hover:text-green-600">
                  About
                </a>
              </li>
              <li>
                <a href="#contact" className="hover:text-green-600">
                  Contact
                </a>
              </li>
              <li>
                <a
                  href="#signin"
                  className="p-2 px-4 rounded-lg border hover:border-green-600 hover:text-green-600 hover:bg-gray-700"
                >
                  Sign In
                </a>
              </li>
            </ul>
          </nav>
        </header>

        <main>{children}</main>
      </body>
    </html>
  )
}
