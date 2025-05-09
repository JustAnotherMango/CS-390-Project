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
        // ✅ Now log in the user after successful registration
        const loginRes = await fetch('http://localhost:5000/login', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: formData.username,
            password: formData.password,
          }),
        });
  
        const loginData = await loginRes.json();
  
        if (loginRes.ok) {
          setMessage('Registration and login successful!');
          window.location.href = '/politicians';
        } else {
          setMessage(loginData.message || 'Registered, but auto-login failed. Please log in manually.');
        }
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
            className="text-white border-b-2 border-white-2 w-8/12 pt-3"
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

          {message && (
            <p
              className={`text-sm mt-2 transition-opacity duration-300 ${
                message.toLowerCase().includes('success') ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {message}
            </p>
          )}

          <p className="text-white cursor-pointer hover:text-green-600 pb-3 underline">Forgot Password</p>
          <button type="submit" className="text-white border-2 border-white-2 rounded-lg py-2 px-10 cursor-pointer bg-green-600 border-green-600 hover:text-green-600 hover:bg-gray-700">Register</button>
          <div className="flex pt-2">
            <p className="text-white pr-1">Already have an account?</p>
            <p className="text-white cursor-pointer hover:text-green-600 pb-3 underline">Login</p>
          </div>
        </form>
  );
}
