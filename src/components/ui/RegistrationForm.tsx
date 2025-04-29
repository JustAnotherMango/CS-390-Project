'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';


export default function RegisterPage() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [message, setMessage] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
  
    if (formData.password !== formData.confirmPassword) {
      setMessage('Passwords do not match');
      return;
    }
  
    try {
      const res = await fetch('http://localhost:5000/register', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        }),
      });
  
      const data = await res.json();
  
      if (res.ok) {
        setMessage(data.message || 'Registration successful!');
        router.push('/politicians'); // success: redirect
      } else {
        setMessage(data.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Error during registration:', error);
      setMessage('Network error. Please try again.');
    }
  };

  return (
        <form className="flex flex-col items-center" onSubmit={handleRegister}>
          <input 
            className="text-white border-b-2 border-white-2 w-8/12"
            type="text"
            name='username'
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
          />
          <input 
            className="text-white border-b-2 border-white-2 w-8/12"
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <input
            className="text-white border-b-2 border-white-2 w-8/12 pt-3"
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <input
            className="text-white border-b-2 border-white-2 w-8/12 pt-3"
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
          <span className="py-2"></span>
          <p className="text-white cursor-pointer hover:text-green-600 pb-3 underline">Forgot Password</p>
          <button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded">Register</button>
          <div className="flex pt-2">
            <p className="text-white pr-1">Don't have an account?</p>
            <p className="text-white cursor-pointer hover:text-green-600 pb-3 underline">Register</p>
          </div>
        </form>
  );
}
