import React from 'react';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-900">
      <header className="sticky top-0 border-b-2 border-green-600 bg-gray-950 p-5 text-white">
        <nav className="flex justify-between items-center">
          <div className="text-2xl font-semibold font-serif">
            <a href="/">Politrade</a>
          </div>
          <ul className="flex space-x-8">
            <li>
              <a href="#politicians" className="hover:text-green-600">
                Politicians
              </a>
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

      <main className="flex-grow container mx-auto p-6">
        {/* Main content removed. */}
      </main>

      <footer className="bg-gray-950 text-white py-6 text-center">
        <p>Footer info here - you made it to the bottom!</p>
      </footer>
    </div>
  );
}
