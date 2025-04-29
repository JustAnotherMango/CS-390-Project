import React from 'react';
import RegistrationForm from '../../components/ui/RegistrationForm';

export default function Home() {
  return (
    <div className="w-full bg-cover bg-center items-center justify-center flex flex-col min-h-screen" style={{ backgroundImage: "url('https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwallpaperaccess.com%2Ffull%2F1393758.jpg&f=1&nofb=1&ipt=74b937665e72726adc97d411b6799bc63c9358be296c369dafa1c510891deb62')" }}>
      <main className="flex-grow container w-1/2 mx-auto p-6 content-center">
        <div className="bg-gray-800 items-center justify-items-center rounded-lg p-4" >
          <h1 className="text-white text-3xl text-center pb-4">Politrades</h1>
          <h2 className="text-white text-center">Create Account</h2>
          <main className="flex-grow container mx-auto p-6">
        <RegistrationForm />
      </main>

          
        </div>
      </main>

      <footer className="bg-gray-950 text-white py-6 text-center w-full">
        <p>Footer info here - you made it to the bottom!</p>
      </footer>
    </div>
  );
}
