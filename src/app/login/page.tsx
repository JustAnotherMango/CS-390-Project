import React from 'react';
import LoginForm from '../../components/ui/LoginForm';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-900">
      <main className="flex-grow container w-1/2 mx-auto p-6 content-center">
        <div className="bg-gray-800 items-center justify-items-center rounded-lg p-4" >
          <h1 className="text-white text-3xl text-center pb-4">Politrades</h1>
          <h2 className="text-white text-center">Sign In</h2>
          <main className="flex-grow container mx-auto p-6">
        <LoginForm />
      </main>

          
        </div>
      </main>

      <footer className="bg-gray-950 text-white py-6 text-center">
        <p>Footer info here - you made it to the bottom!</p>
      </footer>
    </div>
  );
}
