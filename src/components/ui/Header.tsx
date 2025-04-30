"use client"

import Link from "next/link"
import { useAuth } from "@/app/context/AuthContext"
import { useRouter } from "next/navigation"
import { LogOut, User } from "lucide-react"
import { useEffect, useRef, useState } from "react"

export default function Header() {
  const { user, loading, setUser } = useAuth()
  const router = useRouter()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLLIElement>(null)

  const handleLogout = async () => {
    await fetch("/api/logout", { method: "POST", credentials: "include" })
    setUser(null)
    router.push("/")
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  return (
    <header className="sticky top-0 border-b-2 border-green-600 bg-gray-950 p-5 text-white z-10">
      <nav className="flex justify-between items-center max-w-screen mx-auto">
        <Link href="/" className="text-2xl font-semibold font-serif">
          Politrade
        </Link>
        {!loading && (
          <ul className="flex space-x-8 items-center">
            {user && (
              <li>
                <Link href="/politicians" className="hover:text-green-600">
                  Politicians
                </Link>
              </li>
            )}
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
            {!user ? (
              <li>
                <a
                  href="/login"
                  className="p-2 px-4 rounded-lg border hover:border-green-600 hover:text-green-600 hover:bg-gray-700"
                >
                  Sign In
                </a>
              </li>
            ) : (
              <li className="relative" ref={menuRef}>
                <button
                  onClick={() => setMenuOpen((prev) => !prev)}
                  className="flex items-center space-x-2 hover:text-green-600"
                >
                  <User />
                </button>
                {menuOpen && (
                  <div className="absolute right-0 mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-2 z-50">
                    <button
                      onClick={handleLogout}
                      className="flex items-center text-sm hover:text-red-500"
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Sign Out
                    </button>
                  </div>
                )}
              </li>
            )}
          </ul>
        )}
      </nav>
    </header>
  )
}