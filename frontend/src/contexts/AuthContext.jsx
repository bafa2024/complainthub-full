import React, {createContext, useEffect, useState} from 'react';
import apiClient from '../services/apiClient';
import authService from '../services/authService';
import { useNavigate } from 'react-router-dom';

export const AuthContext = createContext();
export function AuthProvider({children}) {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  useEffect(()=>{
    if(token){
      localStorage.setItem('token', token);
      apiClient.defaults.headers.Authorization = `Bearer ${token}`;
    } else {
      localStorage.removeItem('token');
    }
    setLoading(false);
  }, [token]);
  return (
    <AuthContext.Provider value={{token,setToken,loading}}>
      {children}
    </AuthContext.Provider>
  );
}