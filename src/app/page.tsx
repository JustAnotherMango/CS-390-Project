import type React from "react"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-900">

      <header className="sticky top-0 border-b-2 border-green-600 bg-gray-950 p-5 text-white">
        <nav className="flex justify-between items-center max-w-screen">
          <div className="text-2xl font-semibold font-serif">
            <a href="/">Politrade</a>
          </div>
          <ul className="flex space-x-8">
            <li><a href="/dashboard" className="hover:text-green-600">Politicians</a></li>
            <li><a href="#about" className="hover:text-green-600">About</a></li>
            <li><a href="#contact" className="hover:text-green-600">Contact</a></li>
            <li><a href="/login" className="p-2 pl-4 pr-4 rounded-lg border-1 hover:border-green-600 hover:text-green-600 hover:bg-gray-700">Sign In</a></li>
          </ul>
        </nav>
      </header>

      <section className="bg-[url(https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmotionarray.imgix.net%2Fpreview-975047-dOAbHCWmyG-high_0010.jpg&f=1&nofb=1&ipt=56233aa82cc3208e58bf18aabbfd6c7c775d17f5fb46c3f844f19e8dc34696a9&ipo=images)] text-white text-center py-24">
        <div>
          <h1 className="text-5xl font-extrabold font-serif shadow-lg">Check Before You Trade</h1>
          <p className="mt-4 text-lg shadow-lg">We run trades through our neural network to let you know if a trade is likely to succeed or not.</p>
          <button className="mt-8 border-2 border-white text-white py-3 px-6 rounded-lg text-lg hover:bg-green-600 cursor-pointer">
            Get Started
          </button>
        </div>
      </section>

      <section id="getstarted" className="py-16">
        <div className="flex items-center justify-center text-center space-x-4">
          <div className="items-center justify-center text-center">
            <h2 className="text-4xl text-white font-semibold font-serif">About Politrade</h2>
            <p className="mt-4 text-white w-96">Politrade is a web-application with the focus of pulling stock market trades made by politicians and storing them for the public to see.</p>
          </div>
          <div className="px-7"></div>
          <img src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.w5Ee58wup7Nw6bc2u_305AHaEK%26pid%3DApi&f=1&ipt=d67ab1da6c0ad989d9f7293801273a2610ad47c7f61bca91fec9348c61f4e1fe&ipo=images" alt="stock market image" className="w-96 h-80 object-cover"></img>
        </div>
      </section>

      <section id="spacer-1" className="py-1">
        <hr className="border-gray-500 w-3/4 mx-auto"></hr>
      </section>

      <section id="features" className="py-16">
        <h2 className="text-4xl text-center text-white font-semibold font-serif">Features</h2>
        <div className="max-w-screen-xl mx-auto mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-green-600">Politician Search</h3>
            <p className="mt-4 text-white">Search through a variety of politicans to see information about their recent trades.</p>
          </div>
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-green-600">Trend Analysis</h3>
            <p className="mt-4 text-white">View market trends among the top brass of traders.</p>
          </div>
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold text-green-600">Likelihood Analyzer</h3>
            <p className="mt-4 text-white">Our neural network will provide scores based on the likelihood of success in replication trades.</p>
          </div>
        </div>
      </section>

      <section id="spacer-2" className="py-1">
        <hr className="border-gray-500 w-3/4 mx-auto"></hr>
      </section>

      <section id="getstarted" className="py-16">
        <div className="flex items-center justify-center space-x-4">
          
          <img src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.F9YxCgQ2IdBYGS16vozY7AHaE7%26pid%3DApi&f=1&ipt=99d15335221837a5872bd7a218f4ab74edeea493231c1ee0cfe10cebe3f78788&ipo=images" alt="stock market image" className="w-96 h-80 object-cover"></img>
          <div className="px-7"></div>
          <div className="items-center justify-center text-center">
            <h2 className="text-4xl text-center text-white font-semibold font-serif">Ready to Start?</h2>
            <p className="mt-4 text-white">Click below to create an account and get started with us today.</p>
            <button className="mt-8 border-2 border-white text-white py-3 px-6 rounded-lg text-lg hover:bg-gray-700 hover:text-green-600 hover:border-green-600 cursor-pointer">
              Sign Up
            </button>
          </div>
        </div>
      </section>

      <footer className="bg-gray-950 text-white py-6 text-center mt-auto">
        <p>Footer info here - you made it to the bottom!</p>
      </footer>
    </div>
  );
}
