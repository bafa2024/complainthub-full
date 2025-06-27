import React from 'react';
import { Link } from 'react-router-dom';
import './auth.css';

const BrandSignup = () => {
    const handleSubmit = (e) => {
        e.preventDefault();
        alert("Thank you. Your brand registration request has been submitted for review by our administrators.");
    };

    return (
        <div className="auth-container">
            <form onSubmit={handleSubmit} className="auth-form">
                <h2>Register Your Brand</h2>
                <p>Submit your details for approval by our team.</p>
                
                <div className="form-group">
                    <label htmlFor="brandName">Brand Name</label>
                    <input type="text" id="brandName" required />
                </div>
                <div className="form-group">
                    <label htmlFor="workEmail">Your Work Email</label>
                    <input type="email" id="workEmail" required />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" required />
                </div>
                <button type="submit" className="btn btn-primary">Request Approval</button>
            </form>
        </div>
    );
};

export default BrandSignup;