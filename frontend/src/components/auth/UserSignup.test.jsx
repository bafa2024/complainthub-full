import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import '@testing-library/jest-dom';
import UserSignup from './UserSignup';

// Mock AuthContext
const mockSignup = vi.fn();
const mockNavigate = vi.fn();

vi.mock('../../contexts/AuthContext', () => {
  return {
    useAuth: () => ({
      signup: mockSignup,
      mockupMode: false,
    }),
  };
});

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('UserSignup Component', () => {
  beforeEach(() => {
    mockSignup.mockReset();
    mockNavigate.mockReset();
  });

  function renderSignup() {
    return render(
      <BrowserRouter>
        <UserSignup />
      </BrowserRouter>
    );
  }

  it('renders all input fields and submit button', () => {
    renderSignup();
    expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Phone Number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Confirm Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Account/i })).toBeInTheDocument();
  });

  it('shows error if passwords do not match', async () => {
    renderSignup();
    fireEvent.change(screen.getByLabelText(/Full Name/i), { target: { value: 'Test User' } });
    fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/Phone Number/i), { target: { value: '1234567890' } });
    fireEvent.change(screen.getByLabelText(/^Password$/i), { target: { value: 'password1' } });
    fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'password2' } });
    fireEvent.click(screen.getByRole('button', { name: /Create Account/i }));
    expect(await screen.findByText(/Passwords do not match/i)).toBeInTheDocument();
    expect(mockSignup).not.toHaveBeenCalled();
  });

  it('shows error if signup fails', async () => {
    mockSignup.mockRejectedValueOnce(new Error('Signup failed. Please try again.'));
    renderSignup();
    fireEvent.change(screen.getByLabelText(/Full Name/i), { target: { value: 'Test User' } });
    fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/Phone Number/i), { target: { value: '1234567890' } });
    fireEvent.change(screen.getByLabelText(/^Password$/i), { target: { value: 'password' } });
    fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'password' } });
    fireEvent.click(screen.getByRole('button', { name: /Create Account/i }));
    expect(await screen.findByText(/Signup failed. Please try again./i)).toBeInTheDocument();
    expect(mockSignup).toHaveBeenCalled();
  });

  it('calls signup and navigates on successful registration', async () => {
    mockSignup.mockResolvedValueOnce({ message: 'Signup successful' });
    renderSignup();
    fireEvent.change(screen.getByLabelText(/Full Name/i), { target: { value: 'Test User' } });
    fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/Phone Number/i), { target: { value: '1234567890' } });
    fireEvent.change(screen.getByLabelText(/^Password$/i), { target: { value: 'password' } });
    fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'password' } });
    fireEvent.click(screen.getByRole('button', { name: /Create Account/i }));
    await waitFor(() => {
      expect(mockSignup).toHaveBeenCalledWith({
        full_name: 'Test User',
        email: 'test@example.com',
        phone_number: '1234567890',
        password: 'password',
        role: 'user',
      });
      expect(mockNavigate).toHaveBeenCalledWith('/login', { state: { message: 'Signup successful! Please log in.' } });
    });
  });
}); 