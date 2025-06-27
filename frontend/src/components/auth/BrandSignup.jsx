import React, { useState, useContext } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AuthContext } from "../../contexts/AuthContext";

export default function UserSignup() {
  const { signup } = useContext(AuthContext);  // This is the correct way
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    // Validate passwords match
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    
    // Validate password length
    if (form.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }
    
    setLoading(true);
    try {
      console.log("Submitting signup form:", {
        name: form.name,
        email: form.email,
        phone: form.phone,
        password: "***hidden***"
      });
      
      // Use signup from AuthContext
      await signup({
        name: form.name,
        email: form.email,
        phone: form.phone,
        password: form.password,
      });
      
      console.log("Signup successful!");
      
      // Show success and redirect to login
      alert("Account created successfully! Please login with your credentials.");
      navigate("/user/login", { replace: true });
      
    } catch (error) {
      console.error("=== SIGNUP ERROR ===");
      console.error("Full error object:", error);
      
      if (error.response) {
        console.error("Error response status:", error.response.status);
        console.error("Error response data:", error.response.data);
        
        // Handle different error formats
        if (error.response.data?.detail) {
          if (typeof error.response.data.detail === 'string') {
            setError(error.response.data.detail);
          } else if (Array.isArray(error.response.data.detail)) {
            // Pydantic validation errors
            const firstError = error.response.data.detail[0];
            setError(firstError?.msg || "Validation failed");
          } else {
            setError(JSON.stringify(error.response.data.detail));
          }
        } else {
          setError(`Error ${error.response.status}: ${error.response.statusText}`);
        }
      } else if (error.request) {
        console.error("No response received:", error.request);
        setError("No response from server. Please check if the backend is running.");
      } else {
        console.error("Error setting up request:", error.message);
        setError("Error: " + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.authContainer}>
        <div style={styles.authCard}>
          <Link to="/" style={styles.backLink}>
            <span>&larr;</span> Back to Home
          </Link>
          
          <div style={styles.logoSection}>
            <div style={styles.logo}>ComplaintHub</div>
            <p style={styles.tagline}>Voice Your Concerns</p>
          </div>
          
          <div style={styles.authHeader}>
            <h2 style={styles.title}>Create Account</h2>
            <p style={styles.subtitle}>Join thousands getting their complaints resolved</p>
          </div>
          
          {error && (
            <div style={styles.errorMessage}>
              <span style={styles.errorIcon}>⚠️</span> {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.formLabel} htmlFor="name">
                Full Name
              </label>
              <input
                style={styles.formControl}
                type="text"
                id="name"
                name="name"
                placeholder="Enter your full name"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>
            
            <div style={styles.formGroup}>
              <label style={styles.formLabel} htmlFor="email">
                Email Address
              </label>
              <input
                style={styles.formControl}
                type="email"
                id="email"
                name="email"
                placeholder="Enter your email"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
            
            <div style={styles.formGroup}>
              <label style={styles.formLabel} htmlFor="phone">
                Phone Number
              </label>
              <input
                style={styles.formControl}
                type="tel"
                id="phone"
                name="phone"
                placeholder="Enter your phone number"
                value={form.phone}
                onChange={handleChange}
                required
              />
            </div>
            
            <div style={styles.formRow}>
              <div style={styles.formGroupHalf}>
                <label style={styles.formLabel} htmlFor="password">
                  Password
                </label>
                <input
                  style={styles.formControl}
                  type="password"
                  id="password"
                  name="password"
                  placeholder="Min 6 characters"
                  value={form.password}
                  onChange={handleChange}
                  required
                />
              </div>
              
              <div style={styles.formGroupHalf}>
                <label style={styles.formLabel} htmlFor="confirmPassword">
                  Confirm Password
                </label>
                <input
                  style={styles.formControl}
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  placeholder="Confirm password"
                  value={form.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
            
            <div style={styles.terms}>
              <input type="checkbox" id="terms" required style={styles.checkbox} />
              <label htmlFor="terms" style={styles.termsLabel}>
                I agree to the <Link to="/terms" style={styles.link}>Terms of Service</Link> and{' '}
                <Link to="/privacy" style={styles.link}>Privacy Policy</Link>
              </label>
            </div>
            
            <button 
              type="submit" 
              style={styles.btnPrimary}
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
          
          <div style={styles.divider}>
            <span style={styles.dividerText}>OR</span>
          </div>
          
          <div style={styles.socialLogin}>
            <button style={styles.socialBtn}>
              <span>📱</span> Sign up with Phone
            </button>
          </div>
          
          <div style={styles.authFooter}>
            Already have an account? <Link to="/user/login" style={styles.link}>Login</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #3498db 0%, #2c3e50 100%)',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    padding: '20px',
  },
  authContainer: {
    width: '100%',
    maxWidth: '480px',
  },
  authCard: {
    background: 'white',
    padding: '40px',
    borderRadius: '16px',
    boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
  },
  backLink: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    color: '#3498db',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: '500',
    marginBottom: '30px',
    transition: 'all 0.3s',
  },
  logoSection: {
    textAlign: 'center',
    marginBottom: '30px',
  },
  logo: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#3498db',
    marginBottom: '5px',
  },
  tagline: {
    color: '#7f8c8d',
    fontSize: '14px',
  },
  authHeader: {
    textAlign: 'center',
    marginBottom: '30px',
  },
  title: {
    fontSize: '24px',
    color: '#2c3e50',
    marginBottom: '8px',
    fontWeight: '700',
  },
  subtitle: {
    color: '#7f8c8d',
    fontSize: '15px',
  },
  errorMessage: {
    background: '#fee',
    color: '#c33',
    padding: '12px 16px',
    borderRadius: '8px',
    marginBottom: '20px',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  errorIcon: {
    fontSize: '16px',
  },
  form: {
    marginBottom: '20px',
  },
  formGroup: {
    marginBottom: '20px',
  },
  formRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '15px',
    marginBottom: '20px',
  },
  formGroupHalf: {
    width: '100%',
  },
  formLabel: {
    display: 'block',
    marginBottom: '8px',
    fontWeight: '600',
    color: '#2c3e50',
    fontSize: '14px',
  },
  formControl: {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #e1e8ed',
    borderRadius: '8px',
    fontSize: '15px',
    transition: 'all 0.3s',
    outline: 'none',
    backgroundColor: '#f8f9fa',
    boxSizing: 'border-box',
  },
  terms: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '8px',
    marginBottom: '20px',
  },
  checkbox: {
    marginTop: '4px',
    cursor: 'pointer',
  },
  termsLabel: {
    fontSize: '14px',
    color: '#7f8c8d',
    lineHeight: '1.5',
  },
  btnPrimary: {
    width: '100%',
    padding: '14px 24px',
    background: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
    marginTop: '10px',
  },
  divider: {
    textAlign: 'center',
    position: 'relative',
    margin: '25px 0',
  },
  dividerText: {
    background: 'white',
    padding: '0 15px',
    color: '#95a5a6',
    fontSize: '14px',
    position: 'relative',
    display: 'inline-block',
  },
  socialLogin: {
    marginBottom: '25px',
  },
  socialBtn: {
    width: '100%',
    padding: '12px 24px',
    background: 'white',
    color: '#2c3e50',
    border: '2px solid #e1e8ed',
    borderRadius: '8px',
    fontSize: '15px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
  },
  authFooter: {
    textAlign: 'center',
    fontSize: '14px',
    color: '#7f8c8d',
  },
  link: {
    color: '#3498db',
    textDecoration: 'none',
    fontWeight: '600',
  },
};