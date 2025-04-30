"use client"

import React, { createContext, useEffect, useState, useContext } from "react"

type User = {
  username: string
} | null

const AuthContext = createContext<{
  user: User
  loading: boolean
  setUser: (user: User) => void
}>({
  user: null,
  loading: true,
  setUser: () => {},
})

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("/api/me", {
          credentials: "include",
        })
        if (res.ok) {
          const data = await res.json()
          setUser({ username: data.username })
        } else {
          setUser(null)
        }
      } catch {
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)