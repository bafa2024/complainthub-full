import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const UserLogin = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(formData);
            navigate('/dashboard');
        } catch (err) {
            setError(err.message || 'Login failed. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="vh-100" style={{ marginTop: 0, paddingTop: 0 }}>
            <div className="container-fluid h-custom" style={{ marginTop: 0, paddingTop: 0 }}>
                <div className="row d-flex justify-content-center align-items-center h-100" style={{ marginTop: 0, paddingTop: 0 }}>
                    <div className="col-md-9 col-lg-6 col-xl-5">
                        <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-login-form/draw2.webp"
                            className="img-fluid" alt="Sample image" />
                    </div>
                    <div className="col-md-8 col-lg-6 col-xl-4 offset-xl-1">
                        <form onSubmit={handleSubmit}>
                            <div className="d-flex flex-row align-items-center justify-content-center justify-content-lg-start mb-4">
                                <p className="lead fw-normal mb-0 me-3">Sign in with</p>
                                <button type="button" className="btn btn-primary btn-floating mx-1">
                                    <i className="fab fa-facebook-f"></i>
                                </button>
                                <button type="button" className="btn btn-primary btn-floating mx-1">
                                    <i className="fab fa-twitter"></i>
                                </button>
                                <button type="button" className="btn btn-primary btn-floating mx-1">
                                    <i className="fab fa-linkedin-in"></i>
                                </button>
                            </div>

                            <div className="divider d-flex align-items-center my-4">
                                <p className="text-center fw-bold mx-3 mb-0">Or</p>
                            </div>

                            {/* Error Message */}
                            {error && (
                                <div className="alert alert-danger d-flex align-items-center mb-4" role="alert">
                                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                                    <div>{error}</div>
                                </div>
                            )}

                            {/* Email input */}
                            <div className="form-outline mb-4">
                                <input 
                                    type="email" 
                                    id="email" 
                                    name="email"
                                    className="form-control form-control-lg"
                                    placeholder="Enter a valid email address"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                />
                                <label className="form-label" htmlFor="email">Email address</label>
                            </div>

                            {/* Password input */}
                            <div className="form-outline mb-4">
                                <input 
                                    type="password" 
                                    id="password" 
                                    name="password"
                                    className="form-control form-control-lg"
                                    placeholder="Enter password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                />
                                <label className="form-label" htmlFor="password">Password</label>
                            </div>

                            <div className="d-flex justify-content-between align-items-center">
                                {/* Checkbox */}
                                <div className="form-check mb-0">
                                    <input className="form-check-input me-2" type="checkbox" value="" id="form2Example3" />
                                    <label className="form-check-label" htmlFor="form2Example3">
                                        Remember me
                                    </label>
                                </div>
                                <a href="#!" className="text-body">Forgot password?</a>
                            </div>

                            <div className="text-center text-lg-start mt-4 pt-2">
                                <button 
                                    type="submit" 
                                    className="btn btn-primary btn-lg"
                                    style={{ paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                            Logging in...
                                        </>
                                    ) : (
                                        'Login'
                                    )}
                                </button>
                                <p className="small fw-bold mt-2 pt-1 mb-0">
                                    Don't have an account? <Link to="/signup" className="link-danger">Register</Link>
                                </p>
                            </div>

                            {/* Additional Links */}
                            <div className="text-center mt-4">
                                <div className="row g-2">
                                    <div className="col-6">
                                        <Link to="/brand/login" className="btn btn-outline-success btn-sm w-100">
                                            <i className="bi bi-building me-1"></i>
                                            Brand Login
                                        </Link>
                                    </div>
                                    <div className="col-6">
                                        <Link to="/admin/login" className="btn btn-outline-warning btn-sm w-100">
                                            <i className="bi bi-shield-lock me-1"></i>
                                            Admin Login
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            <div className="d-flex flex-column flex-md-row text-center text-md-start justify-content-between py-4 px-4 px-xl-5 bg-primary">
                {/* Copyright */}
                <div className="text-white mb-3 mb-md-0">
                    Copyright © 2024 Complaint Hub. All rights reserved.
                </div>
                {/* Copyright */}

                {/* Right */}
                <div>
                    <a href="#!" className="text-white me-4">
                        <i className="fab fa-facebook-f"></i>
                    </a>
                    <a href="#!" className="text-white me-4">
                        <i className="fab fa-twitter"></i>
                    </a>
                    <a href="#!" className="text-white me-4">
                        <i className="fab fa-google"></i>
                    </a>
                    <a href="#!" className="text-white">
                        <i className="fab fa-linkedin-in"></i>
                    </a>
                </div>
                {/* Right */}
            </div>
        </section>
    );
};

export default UserLogin;