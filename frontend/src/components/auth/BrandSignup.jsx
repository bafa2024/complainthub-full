import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const BrandSignup = () => {
    const [formData, setFormData] = useState({
        brandName: '',
        fullName: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { signup, mockupMode } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match.");
            return;
        }
        setError('');
        setLoading(true);
        try {
            const userData = {
                brand_name: formData.brandName,
                full_name: formData.fullName,
                email: formData.email,
                password: formData.password,
                role: 'brand_user'
            };
            await signup(userData);
            navigate('/brand/login', { state: { message: 'Brand signup successful! Please log in.' } });
        } catch (err) {
            setError(err.message || 'Signup failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (mockupMode) {
        return (
            <section className="vh-100" style={{ marginTop: 0, paddingTop: 0 }}>
                <div className="container-fluid h-custom" style={{ marginTop: 0, paddingTop: 0 }}>
                    <div className="row d-flex justify-content-center align-items-center h-100" style={{ marginTop: 0, paddingTop: 0 }}>
                        <div className="col-md-9 col-lg-6 col-xl-5">
                            <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-login-form/draw2.webp"
                                className="img-fluid" alt="Sample image" />
                        </div>
                        <div className="col-md-8 col-lg-6 col-xl-4 offset-xl-1">
                            <div className="text-center mb-4">
                                <h1 className="h3 fw-bold text-dark mb-2">🎭 Mockup Mode Active</h1>
                                <div className="alert alert-info d-flex align-items-center" role="alert">
                                    <i className="bi bi-info-circle me-2"></i>
                                    <div><strong>Authentication is disabled.</strong> You can access all sections directly.</div>
                                </div>
                            </div>
                            
                            <div className="mb-4">
                                <h4 className="h5 fw-semibold mb-3">Quick Access:</h4>
                                <div className="row g-2">
                                    <div className="col-12">
                                        <button 
                                            onClick={() => navigate('/brand/dashboard')} 
                                            className="btn btn-success w-100"
                                        >
                                            <i className="bi bi-speedometer2 me-1"></i>
                                            Brand Dashboard
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="alert alert-light" role="alert">
                                <i className="bi bi-lightbulb me-2"></i>
                                <small className="text-muted">
                                    Use the role switcher in the bottom-right corner to change your role and see different views.
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="d-flex flex-column flex-md-row text-center text-md-start justify-content-between py-4 px-4 px-xl-5 bg-primary">
                    <div className="text-white mb-3 mb-md-0">
                        Copyright © 2024 Complaint Hub. All rights reserved.
                    </div>
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
                </div>
            </section>
        );
    }

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
                                <p className="lead fw-normal mb-0 me-3">Brand sign up with</p>
                                <button type="button" className="btn btn-success btn-floating mx-1">
                                    <i className="fab fa-facebook-f"></i>
                                </button>
                                <button type="button" className="btn btn-success btn-floating mx-1">
                                    <i className="fab fa-twitter"></i>
                                </button>
                                <button type="button" className="btn btn-success btn-floating mx-1">
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

                            {/* Brand Name input */}
                            <div className="form-outline mb-4">
                                <input 
                                    type="text" 
                                    id="brandName" 
                                    name="brandName"
                                    className="form-control form-control-lg"
                                    placeholder="Enter your brand name"
                                    value={formData.brandName}
                                    onChange={handleChange}
                                    required
                                    autoComplete="organization"
                                />
                                <label className="form-label" htmlFor="brandName">Brand name</label>
                            </div>

                            {/* Full Name input */}
                            <div className="form-outline mb-4">
                                <input 
                                    type="text" 
                                    id="fullName" 
                                    name="fullName"
                                    className="form-control form-control-lg"
                                    placeholder="Enter your full name"
                                    value={formData.fullName}
                                    onChange={handleChange}
                                    required
                                    autoComplete="name"
                                />
                                <label className="form-label" htmlFor="fullName">Your name</label>
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
                                    autoComplete="email"
                                />
                                <label className="form-label" htmlFor="email">Work email</label>
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
                                    autoComplete="new-password"
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
                                    autoComplete="new-password"
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
                                    className="btn btn-success btn-lg"
                                    style={{ paddingLeft: '2.5rem', paddingRight: '2.5rem' }}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                            Creating Brand Account...
                                        </>
                                    ) : (
                                        'Create Brand Account'
                                    )}
                                </button>
                                <p className="small fw-bold mt-2 pt-1 mb-0">
                                    Already have a brand account? <Link to="/brand/login" className="link-danger">Brand Login</Link>
                                </p>
                            </div>

                            {/* Additional Links */}
                            <div className="text-center">
                                <div className="row g-2">
                                    <div className="col-6">
                                        <Link to="/signup" className="btn btn-outline-primary btn-sm w-100">
                                            <i className="bi bi-person me-1"></i>
                                            Customer Signup
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

export default BrandSignup;