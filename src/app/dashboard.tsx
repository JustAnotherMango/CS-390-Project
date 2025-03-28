"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { LogOut, Search } from "lucide-react"
import { useState, useEffect } from "react"

// Define the Politician type based on your database structure
interface Politician {
    PoliticianID: number
    Name: string
    Party: string
    Position: string
}

export default function Dashboard() {
    const [searchTerm, setSearchTerm] = useState("")
    const [searchResults, setSearchResults] = useState<Politician[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState("")
    const [backendStatus, setBackendStatus] = useState<"connecting" | "connected" | "error">("connecting")

    // Function to fetch politicians based on search term
    const searchPoliticians = async (term: string) => {
        if (!term.trim()) {
            setSearchResults([])
            return
        }

        setIsLoading(true)
        setError("")

        try {
            // Replace with your Flask API URL
            const response = await fetch("http://127.0.0.1:5000")

            if (!response.ok) {
                throw new Error("Failed to fetch data")
            }

            const data = await response.json()

            // Filter politicians by name containing the search term
            const filteredResults = data.filter((politician: Politician) =>
                politician.Name.toLowerCase().includes(term.toLowerCase()),
            )

            setSearchResults(filteredResults)
            setBackendStatus("connected")
        } catch (err) {
            console.error("Error fetching politicians:", err)
            setError("Failed to fetch politicians. Please try again.")
            setBackendStatus("error")
        } finally {
            setIsLoading(false)
        }
    }

    // Check backend connection on load
    useEffect(() => {
        const checkBackend = async () => {
            try {
                const response = await fetch("http://127.0.0.1:5000")
                if (response.ok) {
                    setBackendStatus("connected")
                } else {
                    setBackendStatus("error")
                }
            } catch (err) {
                setBackendStatus("error")
            }
        }

        checkBackend()
    }, [])

    // Handle search input changes
    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value
        setSearchTerm(value)
    }

    // Debounce search to avoid too many API calls
    useEffect(() => {
        const timer = setTimeout(() => {
            if (backendStatus === "connected") {
                searchPoliticians(searchTerm)
            }
        }, 300)

        return () => clearTimeout(timer)
    }, [searchTerm, backendStatus])

    return (
        <div className="min-h-screen bg-background flex flex-col">
            <header className="w-full p-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div className="flex items-center">
                        <div
                            className={`h-3 w-3 rounded-full mr-2 ${backendStatus === "connected"
                                    ? "bg-green-500"
                                    : backendStatus === "connecting"
                                        ? "bg-yellow-500"
                                        : "bg-red-500"
                                }`}
                        ></div>
                        <span className="text-sm text-muted-foreground">
                            {backendStatus === "connected"
                                ? "Backend Connected"
                                : backendStatus === "connecting"
                                    ? "Connecting to Backend..."
                                    : "Backend Not Connected"}
                        </span>
                    </div>
                    <Button variant="ghost" size="icon">
                        <LogOut className="h-5 w-5" />
                        <span className="sr-only">Logout</span>
                    </Button>
                </div>
            </header>
            <main className="flex-grow flex flex-col items-center px-4 py-8">
                <div className="max-w-md w-full mb-8">
                    <h1 className="text-2xl font-bold text-center mb-6">Politicians Database</h1>
                    <div className="relative">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            type="search"
                            placeholder="Search politicians..."
                            className="pl-8"
                            value={searchTerm}
                            onChange={handleSearchChange}
                        />
                    </div>
                </div>

                {/* Search Results */}
                <div className="w-full max-w-2xl">
                    {isLoading && <p className="text-center">Loading...</p>}

                    {error && <p className="text-center text-red-500">{error}</p>}

                    {!isLoading && !error && searchResults.length === 0 && searchTerm && (
                        <p className="text-center text-muted-foreground">No politicians found matching "{searchTerm}"</p>
                    )}

                    {searchResults.length > 0 && (
                        <div className="space-y-4">
                            <h2 className="text-xl font-semibold">Search Results</h2>
                            {searchResults.map((politician) => (
                                <Card key={politician.PoliticianID} className="p-4">
                                    <h3 className="font-medium">{politician.Name}</h3>
                                    <p className="text-sm text-muted-foreground">Party: {politician.Party}</p>
                                    <p className="text-sm text-muted-foreground">Position: {politician.Position}</p>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}

