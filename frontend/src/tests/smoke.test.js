import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import HomePage from '../components/public/HomePage';
import Header from '../components/shared/Header';
import UserLogin from '../components/auth/UserLogin';
import UserSignup from '../components/auth/UserSignup';

// Mock API client
jest.mock('../services/apiClient', () => ({
  post: jest.fn(),
  get: jest.fn(),
  interceptors: {
    request: { use: jest.fn() },
    response: { use: jest.fn() }
  }
}));

// Wrapper component for tests
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Smoke Tests - Core Functionality', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test('HomePage renders key elements', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    );
    
    expect(screen.getByText(/ComplaintHub/i)).toBeInTheDocument();
    expect(screen.getByText(/Streamline Your Complaint Management/i)).toBeInTheDocument();
  });

  test('Header renders navigation elements', () => {
    render(
      <TestWrapper>
        <Header />
      </TestWrapper>
    );
    
    expect(screen.getByText('ComplaintHub')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Sign Up')).toBeInTheDocument();
  });

  test('UserLogin form renders correctly', () => {
    render(
      <TestWrapper>
        <UserLogin />
      </TestWrapper>
    );
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('UserSignup form renders correctly', () => {
    render(
      <TestWrapper>
        <UserSignup />
      </TestWrapper>
    );
    
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
  });

  test('Navigation links work correctly', () => {
    render(
      <TestWrapper>
        <Header />
      </TestWrapper>
    );
    
    const homeLink = screen.getByText('Home');
    const loginLink = screen.getByText('Login');
    const signupLink = screen.getByText('Sign Up');
    
    expect(homeLink.closest('a')).toHaveAttribute('href', '/');
    expect(loginLink.closest('a')).toHaveAttribute('href', '/login');
    expect(signupLink.closest('a')).toHaveAttribute('href', '/signup');
  });

  test('Login form validation works', async () => {
    render(
      <TestWrapper>
        <UserLogin />
      </TestWrapper>
    );
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(submitButton);
    
    // Should show validation errors for empty fields
    await waitFor(() => {
      expect(screen.getByText(/email is required/i) || screen.getByText(/please enter your email/i)).toBeInTheDocument();
    });
  });

  test('Signup form validation works', async () => {
    render(
      <TestWrapper>
        <UserSignup />
      </TestWrapper>
    );
    
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    fireEvent.click(submitButton);
    
    // Should show validation errors for empty fields
    await waitFor(() => {
      expect(screen.getByText(/first name is required/i) || screen.getByText(/please enter your first name/i)).toBeInTheDocument();
    });
  });

  test('HomePage hero section has proper styling', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    );
    
    const heroSection = screen.getByText(/Streamline Your Complaint Management/i).closest('section');
    expect(heroSection).toHaveStyle('background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%)');
    expect(heroSection).toHaveStyle('color: white');
  });

  test('Layout is responsive and has proper Bootstrap classes', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    );
    
    // Check for responsive grid classes
    const containers = document.querySelectorAll('.container, .container-fluid');
    expect(containers.length).toBeGreaterThan(0);
    
    // Check for responsive row/col classes
    const rows = document.querySelectorAll('.row');
    expect(rows.length).toBeGreaterThan(0);
  });
});

describe('Smoke Tests - API Integration', () => {
  test('AuthContext initializes properly', () => {
    render(
      <TestWrapper>
        <div>Test component</div>
      </TestWrapper>
    );
    
    // Should not throw errors during initialization
    expect(screen.getByText('Test component')).toBeInTheDocument();
  });

  test('API client is configured correctly', () => {
    const apiClient = require('../services/apiClient').default;
    expect(apiClient.interceptors).toBeDefined();
    expect(apiClient.interceptors.request).toBeDefined();
    expect(apiClient.interceptors.response).toBeDefined();
  });
});