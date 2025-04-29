"use client";
import type React from "react";
import {useEffect, useState} from 'react';

export default function Home() {

  return (
    <div className="flex flex-col min-h-screen bg-gray-900">
      <section
        className="bg-[url(https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmotionarray.imgix.net%2Fpreview-975047-dOAbHCWmyG-high_0010.jpg&f=1&nofb=1&ipt=56233aa82cc3208e58bf18aabbfd6c7c775d17f5fb46c3f844f19e8dc34696a9&ipo=images)]
                   text-white text-center py-24"
      >
        <h1 className="text-5xl font-extrabold font-serif shadow-lg">
          Check Before You Trade
        </h1>
        <p className="mt-4 text-lg shadow-lg">
          We run trades through our neural network to let you know if a trade is
          likely to succeed or not.
        </p>
        <a href="/login">
          <button className="mt-8 border-2 border-white text-white py-3 px-6 rounded-lg text-lg hover:bg-green-600 cursor-pointer">
            Get Started
          </button>
        </a>
      </section>

      <section id="about" className="py-16">
        <div className="flex flex-col md:flex-row items-center justify-center text-center space-y-8 md:space-y-0 md:space-x-8">
          <div>
            <h2 className="text-4xl text-white font-semibold font-serif">
              About Politrade
            </h2>
            <p className="mt-4 text-white max-w-md">
              Politrade is a web-application focused on pulling stock market trades 
              made by politicians and storing them for the public to see.
            </p>
          </div>
          <img
            src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.w5Ee58wup7Nw6bc2u_305AHaEK%26pid%3DApi&f=1&ipo=images"
            alt="stock market image"
            className="w-72 h-56 object-cover rounded-lg shadow-lg"
          />
        </div>
      </section>

      <section className="py-1">
        <hr className="border-gray-500 w-3/4 mx-auto" />
      </section>

      <section id="features" className="py-16">
        <h2 className="text-4xl text-center text-white font-semibold font-serif">
          Features
        </h2>
        <div className="max-w-screen-xl mx-auto mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-green-600">
              Politician Search
            </h3>
            <p className="mt-4 text-white">
              Search through politicians to see information about their recent trades.
            </p>
          </div>
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-green-600">
              Trend Analysis
            </h3>
            <p className="mt-4 text-white">
              View market trends among the top brass of traders.
            </p>
          </div>
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-green-600">
              Likelihood Analyzer
            </h3>
            <p className="mt-4 text-white">
              Our neural network provides scores based on likelihood of success.
            </p>
          </div>
        </div>
      </section>

      <section className="py-1">
        <hr className="border-gray-500 w-3/4 mx-auto" />
      </section>

      <section className="py-16 flex flex-col items-center space-y-8">
        <img
          src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.F9YxCgQ2IdBYGS16vozY7AHaE7%26pid%3DApi&f=1&ipo=images"
          alt="stock market image"
          className="w-72 h-56 object-cover rounded-lg shadow-lg"
        />
        <div className="text-center max-w-md">
          <h2 className="text-4xl text-white font-semibold font-serif">
            Ready to Start?
          </h2>
          <p className="mt-4 text-white">
            Create an account and get started with us today.
          </p>
          <a href="/registration">
            <button className="mt-8 border-2 border-white text-white py-3 px-6 rounded-lg text-lg hover:bg-gray-700 hover:text-green-600 hover:border-green-600 cursor-pointer">
              Sign Up
            </button>
          </a>
        </div>
      </section>

      <footer className="bg-gray-950 text-white py-6 text-center mt-auto">
        <p>Footer info here – you made it to the bottom!</p>
      </footer>
    </div>
  )
}
