"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";

// npm install lucide-react
import { CheckSquare } from "lucide-react";



export default function AboutPage() {
  const [user, setUser] = useState<{ username: string } | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("http://localhost:5000/me", {
          credentials: "include",
        });

        if (res.ok) {
          const data = await res.json();
          setUser({ username: data.username });
        } else {
          setUser(null);
        }
      } catch (error) {
        console.error("Failed to fetch user:", error);
        setUser(null);
      }
    };

    fetchUser();
  }, []);

  return (
      <div className="flex flex-col min-h-screen bg-gray-900 text-white">
          {/* Header */}
          <header className="sticky top-0 border-b-2 border-green-600 bg-gray-950 p-5 text-white">
              <nav className="flex justify-between items-center max-w-screen">
                  <div className="text-2xl font-semibold font-serif">
                      <Link href="/">Politrade</Link>
                  </div>
                  <ul className="flex space-x-8">
                      <li>
                          <Link href="/dashboard" className="hover:text-green-600">Politicians</Link>
                      </li>
                      <li>
                          <Link href="/about" className="hover:text-green-600">About</Link>
                      </li>
                      <li>
                          <a href="#contact" className="hover:text-green-600">Contact</a>
                      </li>
                      {user ? (
                          <li className="p-2 pl-4 pr-4 rounded-lg border-1 text-green-500 bg-gray-800 font-medium hover:text-red-700 hover:cursor-pointer">
                              <button
                                  onClick={async () => {
                                      try {
                                          const res = await fetch("http://localhost:5000/logout", {
                                              method: "POST",
                                              credentials: "include",
                                          });
                                          if (res.ok) {
                                              setUser(null);
                                          } else {
                                              console.error("Logout failed");
                                          }
                                      } catch (err) {
                                          console.error("Logout error:", err);
                                      }
                                  }}
                              >
                                  {user.username} (Logout)
                              </button>
                          </li>
                      ) : (
                          <li>
                              <Link
                                  href="/login"
                                  className="p-2 pl-4 pr-4 rounded-lg border-1 hover:border-green-600 hover:text-green-600 hover:bg-gray-700"
                              >
                                  Sign In
                              </Link>
                          </li>
                      )}
                  </ul>
              </nav>
          </header>

          {/* About Content */}
          <main className="flex-grow container mx-auto px-6 py-16">
              <h1 className="text-5xl font-bold font-serif text-center mb-12">About Politrade</h1>
              <br/>
              <div className="max-w-3xl mx-auto flex flex-col gap-y-10 text-gray-200">

                  <div className="flex items-start gap-x-6">
                      <CheckSquare className="text-green-500 w-6 h-6 mr-4 shrink-0" />
                      <p>
                          <span className="font-medium text-white">Politrade</span> is a data-driven platform built to
                          increase
                          transparency around stock trades made by U.S. politicians. Using publicly available
                          disclosures, we
                          collect, process, and present financial transactions made by senators, representatives, and
                          other
                          political figures.
                      </p>
                  </div>
                  <br/>
                  <div className="flex items-start gap-x-6">
                      <CheckSquare className="text-green-500 w-6 h-6 shrink-0"/>
                      <p>
                          We apply a custom neural network model to assign confidence scores to these trades, helping
                          users better understand patterns, behaviors, and potential insider advantages.
                      </p>
                  </div>
                  <br/>
                  <div className="flex items-start gap-x-6">
                      <CheckSquare className="text-green-500 w-6 h-6 shrink-0"/>
                      <p>
                          Our goal is to empower investors, researchers, and citizens with meaningful insights into
                          political trading behavior, while promoting greater accountability and awareness.
                      </p>
                  </div>
                  <br/>
                  <div className="flex items-start gap-x-6">
                      <CheckSquare className="text-green-500 w-6 h-6 shrink-0"/>
                      <p className="italic text-green-400"> Transparency creates trust. Data makes it actionable.
                      </p>
                  </div>

              </div>

              <div className="flex justify-center mt-12">
                  <Link href="/dashboard">
                      <button
                          className="px-6 py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold transition cursor-pointer">
                          Get Started
                      </button>


                  </Link>
              </div>

          </main>


          {/* Footer */
          }
          <footer className="bg-gray-950 text-white py-6 text-center mt-auto">
              <p>© 2025 Politrade — All Rights Reserved.</p>
          </footer>
      </div>


  );
}
