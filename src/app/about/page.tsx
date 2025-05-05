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
