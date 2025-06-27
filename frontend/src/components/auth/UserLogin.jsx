// src/components/auth/UserSignup.jsx

import React, { useState, useContext } from 'react';
import authService from '../../services/authService';
import { AuthContext } from '../../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import './auth.css';

export default function UserSignup() {
  const navigate = useNavigate();
  const { setToken } = useContext(AuthContext);
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');

  const handleChange = e =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      const { access_token } = await authService.signup({
        name: form.name,
        email: form.email,
        phone: form.phone,
        password: form.password
      });
      setToken(access_token);
      navigate('/user/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed');
    }
  };

  return (
    <div className="signup-container">
      <form className="signup-form" onSubmit={handleSubmit}>
        <h2>Create Your Account</h2>
        {error && <div className="error">{error}</div>}
        <label>
          <span>Name</span>
          <input
            name="name"
            placeholder="Full Name"
            type="text"
            value={form.name}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          <span>Email</span>
          <input
            name="email"
            placeholder="Email Address"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          <span>Phone</span>
          <input
            name="phone"
            placeholder="Phone Number"
            type="tel"
            value={form.phone}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          <span>Password</span>
          <input
            name="password"
            placeholder="Password"
            type="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          <span>Confirm Password</span>
          <input
            name="confirmPassword"
            placeholder="Confirm Password"
            type="password"
            value={form.confirmPassword}
            onChange={handleChange}
            required
          />
        </label>
        <button type="submit">Sign Up</button>
        <p>
          Already have an account? <Link to="/user/login">Login here</Link>
        </p>
      </form>
    </div>
  );
}
