import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
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

describe('Authentication Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
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
    expect(screen.getAllByLabelText(/password/i).length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
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
      const errorElements = screen.queryAllByText(/required/i);
      expect(errorElements.length).toBeGreaterThan(0);
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
      const errorElements = screen.queryAllByText(/required/i);
      expect(errorElements.length).toBeGreaterThan(0);
    });
  });

  test('Login form accepts input', () => {
    render(
      <TestWrapper>
        <UserLogin />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('password123');
  });

  test('Signup form accepts input', () => {
    render(
      <TestWrapper>
        <UserSignup />
      </TestWrapper>
    );
    
    const firstNameInput = screen.getByLabelText(/first name/i);
    const lastNameInput = screen.getByLabelText(/last name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInputs = screen.getAllByLabelText(/password/i);
    const passwordInput = passwordInputs[0]; // Get the first password field
    
    fireEvent.change(firstNameInput, { target: { value: 'John' } });
    fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
    fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(firstNameInput.value).toBe('John');
    expect(lastNameInput.value).toBe('Doe');
    expect(emailInput.value).toBe('john@example.com');
    expect(passwordInput.value).toBe('password123');
  });
});