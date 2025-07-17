import React, { useState } from "react";

export default function UserLogin({ onLogin }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const params = new URLSearchParams();
      params.append("username", form.email);
      params.append("password", form.password);

      const resp = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: params,
      });
      if (resp.ok) {
        const data = await resp.json();
        localStorage.setItem("token", data.access_token);
        setMessage("Login successful!");
        if (onLogin) onLogin();
      } else {
        const err = await resp.json();
        setMessage(err.detail || "Login failed!");
      }
    } catch (err) {
      setMessage("Login failed: " + err.message);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="card shadow-lg" style={{ maxWidth: "400px", width: "100%" }}>
        <div className="card-body p-4">
          <a href="/" className="btn btn-link text-decoration-none mb-3">
            <i className="bi bi-arrow-left"></i> Back to Home
          </a>
          <div className="text-center mb-4">
            <h2 className="h3 mb-2">Login to ComplaintHub</h2>
            <p className="text-muted">Enter your email and password to access your account.</p>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label" htmlFor="email">Email Address</label>
              <input
                className="form-control"
                type="email"
                id="email"
                name="email"
                autoComplete="username"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="password">Password</label>
              <input
                className="form-control"
                type="password"
                id="password"
                name="password"
                autoComplete="current-password"
                value={form.password}
                onChange={handleChange}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary w-100 mb-3">
              Login
            </button>
            {message && (
              <div className={`alert ${message.includes('successful') ? 'alert-success' : 'alert-danger'}`}>
                {message}
              </div>
            )}
          </form>
          <div className="text-center mt-3">
            <small className="text-muted">
              Don't have an account? <a href="/signup" className="text-decoration-none">Sign Up</a>
            </small>
          </div>
        </div>
      </div>
    </div>
  );
}
