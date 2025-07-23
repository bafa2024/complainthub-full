import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import HomePage from '../components/public/HomePage';
import Header from '../components/shared/Header';

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

describe('Layout Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test('HomePage renders with correct layout structure', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    );
    
    // Check hero section exists with correct text
    expect(screen.getByText(/Voice Your Concerns/i)).toBeInTheDocument();
    expect(screen.getByText(/Making Brands Accountable, One Voice at a Time/i)).toBeInTheDocument();
    
    // Check call to action buttons exist (use getAllByText for multiple instances)
    expect(screen.getAllByText(/Get Started/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/How It Works/i)).toBeInTheDocument();
    
    // Check layout containers
    const containers = document.querySelectorAll('.container, .container-fluid');
    expect(containers.length).toBeGreaterThan(0);
  });

  test('Header has proper navigation structure', () => {
    render(
      <TestWrapper>
        <Header />
      </TestWrapper>
    );
    
    // Check brand name
    expect(screen.getByText('ComplaintHub')).toBeInTheDocument();
    
    // Check navigation links (based on actual Header component)
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Sign Up')).toBeInTheDocument();
    
    // Check header is fixed
    const header = document.querySelector('header');
    if (header) {
      const styles = window.getComputedStyle(header);
      expect(styles.position).toBe('fixed');
    }
  });

  test('HomePage hero section has gradient background', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    );
    
    const heroSection = screen.getByText(/Voice Your Concerns/i).closest('section');
    expect(heroSection).toHaveStyle('background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%)');
    expect(heroSection).toHaveStyle('color: rgb(255, 255, 255)');
  });

  test('Layout is responsive with Bootstrap grid', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    );
    
    // Check for Bootstrap grid classes
    const rows = document.querySelectorAll('.row');
    expect(rows.length).toBeGreaterThan(0);
    
    const cols = document.querySelectorAll('[class*="col-"]');
    expect(cols.length).toBeGreaterThan(0);
  });

  test('Features section displays cards correctly', () => {
    render(
      <TestWrapper>
        <HomePage />
      </TestWrapper>
    );
    
    // Check for actual feature cards from the HomePage
    expect(screen.getByText(/Voice Complaints/i)).toBeInTheDocument();
    expect(screen.getByText(/Multi-Channel Support/i)).toBeInTheDocument();
    expect(screen.getByText(/Real-Time Tracking/i)).toBeInTheDocument();
  });
});