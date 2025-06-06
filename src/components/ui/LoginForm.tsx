'use client';

import { useState, useEffect } from 'react';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('http://localhost:5000/login', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();
    if (res.ok) {
      setMessage('Login successful!');
      window.location.href = '/politicians';
    } else {
      setMessage(data.message || 'Login failed');
    }
  };

  useEffect(() => {
    if (message) {
      const timeout = setTimeout(() => setMessage(''), 4000);
      return () => clearTimeout(timeout);
    }
  }, [message]);

  return (
    <form className="flex flex-col items-center" onSubmit={handleLogin}>
      <input 
        className="text-white border-b-2 border-white-2 w-8/12"
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
      />
      <input
        className="text-white border-b-2 border-white-2 w-8/12 pt-3"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <span className="py-2"></span>
      <p className="text-white cursor-pointer hover:text-green-600 pb-3 underline">Forgot Password</p>
      <button
        className="text-white border-2 border-white-2 rounded-lg py-2 px-10 cursor-pointer bg-green-600 border-green-600 hover:text-green-600 hover:bg-gray-700"
        type="submit"
      >
        Login
      </button>

      {message && (
        <p
          className={`text-sm mt-3 transition-opacity duration-300 ${
            message.toLowerCase().includes('success') ? 'text-green-400' : 'text-red-400'
          }`}
        >
          {message}
        </p>
      )}

      <div className="flex pt-2">
        <p className="text-white pr-1">Don't have an account?</p>
        <a href="/registration">
          <p className="text-white cursor-pointer hover:text-green-600 pb-3 underline">Register</p>
        </a>
      </div>
    </form>
  );
}