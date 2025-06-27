import React from 'react';
import { Link } from 'react-router-dom';
export default function Layout({title, children}) {
  return (
    <div>
      <header style={{padding:'1rem', background:'#eee'}}>
        <Link to="/admin/dashboard">Dashboard</Link> |
        <Link to="/admin/brands">Brands</Link> |
        <Link to="/admin/users">Users</Link> |
        <Link to="/admin/settings">Settings</Link> |
        <Link to="/admin/reports">Reports</Link>
      </header>
      <h1 style={{padding:'1rem'}}>{title}</h1>
      <div style={{padding:'1rem'}}>{children}</div>
    </div>
  );
}