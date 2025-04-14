'use client';

import { useState } from 'react';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();
    if (res.ok) {
      setMessage('Login successful!');
      // Redirect or set cookie/token here
    } else {
      setMessage(data.message || 'Login failed');
    }
  };

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
        <button className="text-white border-2 border-white-2 rounded-lg py-2 px-5 cursor-pointer bg-green-600 border-green-600 hover:text-green-600 hover:bg-gray-700" type="submit">Login</button>
        <p>{message}</p>
        <p className="text-white cursor-pointer hover:text-green-600 pt-2">Forgot Password</p>
        <p className="text-white cursor-pointer hover:text-green-600">Create Account</p>
      </form>
  );
}
