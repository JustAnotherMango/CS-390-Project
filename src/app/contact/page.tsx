"use client"

import React, { useState } from "react"
import { Card } from "@/components/ui/card"

export default function ContactUsPage() {
    const [name, setName] = useState("")
    const [email, setEmail] = useState("")
    const [message, setMessage] = useState("")
    const [status, setStatus] = useState<"idle" | "sending" | "success" | "error">("idle")

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setStatus("sending")
        try {
            const res = await fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, message }),
            })
            if (!res.ok) throw new Error('Network response was not ok')
            setStatus("success")
            setName("")
            setEmail("")
            setMessage("")
        } catch (err) {
            console.error(err)
            setStatus("error")
        }
    }

    return (
        <div className="max-w-2xl mx-auto p-6">
            <Card className="p-6 space-y-6 bg-gray-900 text-white">
                <h2 className="text-2xl font-bold">Contact Us</h2>
                <form onSubmit={handleSubmit} className="space-y-4 justify-items-center">
                    <div>
                        <label htmlFor="name" className="block text-sm font-medium mb-1">Name</label>
                        <input
                            id="name"
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                            className="w-full p-2 rounded bg-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Your name"
                        />
                    </div>
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full p-2 rounded bg-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="you@example.com"
                        />
                    </div>
                    <div>
                        <label htmlFor="message" className="block text-sm font-medium mb-1">Message</label>
                        <textarea
                            id="message"
                            rows={4}
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            required
                            className="w-full p-2 rounded bg-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Your message..."
                        />
                    </div>
                    <div>
                        <button
                            type="submit"
                            disabled={status === "sending"}
                            className="text-white border-2 border-white-2 rounded-lg py-2 px-10 cursor-pointer bg-green-600 border-green-600 hover:text-green-600 hover:bg-gray-700"
                            >
                            {status === "sending" ? "Sending..." : "Send Message"}
                        </button>
                    </div>
                    {status === "success" && (
                        <p className="text-green-400">Thanks! Your message has been sent.</p>
                    )}
                    {status === "error" && (
                        <p className="text-red-400">Oops! Something went wrong. Please try again.</p>
                    )}
                </form>
            </Card>
        </div>
    )
}
