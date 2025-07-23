import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const UserSignup = () => {
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { signup } = useAuth();
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
        
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        
        setLoading(true);
        try {
            await signup(formData);
            navigate('/dashboard');
        } catch (err) {
            setError(err.message || 'Signup failed. Please try again.');
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
                        <form onSubmit={handleSubmit} className="needs-validation" noValidate>
                            <div className="d-flex flex-row align-items-center justify-content-center justify-content-lg-start mb-4">
                                <p className="lead fw-normal mb-0 me-3">Sign up with</p>
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

                            {/* Name inputs */}
                            <div className="row g-3 mb-4">
                                <div className="col-md-6">
                                    <div className="form-outline">
                                        <input 
                                            type="text" 
                                            id="firstName" 
                                            name="firstName"
                                            className="form-control form-control-lg"
                                            placeholder="First name"
                                            value={formData.firstName}
                                            onChange={handleChange}
                                            required
                                        />
                                        <label className="form-label" htmlFor="firstName">First name</label>
                                    </div>
                                </div>
                                <div className="col-md-6">
                                    <div className="form-outline">
                                        <input 
                                            type="text" 
                                            id="lastName" 
                                            name="lastName"
                                            className="form-control form-control-lg"
                                            placeholder="Last name"
                                            value={formData.lastName}
                                            onChange={handleChange}
                                            required
                                        />
                                        <label className="form-label" htmlFor="lastName">Last name</label>
                                    </div>
                                </div>
                            </div>

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

                            {/* Phone input */}
                            <div className="form-outline mb-4">
                                <input 
                                    type="tel" 
                                    id="phone" 
                                    name="phone"
                                    className="form-control form-control-lg"
                                    placeholder="Enter phone number"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    required
                                />
                                <label className="form-label" htmlFor="phone">Phone number</label>
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
                                    minLength="6"
                                />
                                <label className="form-label" htmlFor="password">Password</label>
                            </div>

                            {/* Confirm Password input */}
                            <div className="form-outline mb-4">
                                <input 
                                    type="password" 
                                    id="confirmPassword" 
                                    name="confirmPassword"
                                    className="form-control form-control-lg"
                                    placeholder="Confirm password"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    required
                                    minLength="6"
                                />
                                <label className="form-label" htmlFor="confirmPassword">Confirm password</label>
                            </div>

                            {/* Terms checkbox */}
                            <div className="form-check mb-4">
                                <input className="form-check-input me-2" type="checkbox" value="" id="terms" required />
                                <label className="form-check-label" htmlFor="terms">
                                    I agree to the <a href="#!" className="text-body">Terms of Service</a>
                                </label>
                            </div>

                            {/* Submit Button */}
                            <div className="text-center text-lg-start mb-4">
                                <button 
                                    type="submit" 
                                    className="btn btn-primary btn-lg"
                                    style={{ paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                            Creating Account...
                                        </>
                                    ) : (
                                        'Register'
                                    )}
                                </button>
                                <p className="small fw-bold mt-2 pt-1 mb-0">
                                    Already have an account? <Link to="/login" className="link-danger">Login</Link>
                                </p>
                            </div>

                            {/* Additional Links */}
                            <div className="text-center">
                                <div className="row g-2">
                                    <div className="col-6">
                                        <Link to="/brand/signup" className="btn btn-outline-secondary btn-sm w-100">
                                            <i className="bi bi-building me-1"></i>
                                            Brand Signup
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

export default UserSignup;