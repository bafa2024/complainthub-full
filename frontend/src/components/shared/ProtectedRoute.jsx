import React, {useContext} from 'react';
import {Navigate, Outlet} from 'react-router-dom';
import {AuthContext} from '../../contexts/AuthContext';

export default function ProtectedRoute(){
  const {token, loading} = useContext(AuthContext);
  if(loading) return <div>Loading...</div>;
  if(!token) return <Navigate to="/admin/login" />;
  return <Outlet />;
}