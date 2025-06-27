import React, { useState, useContext, useEffect } from 'react';
import apiClient from '../../services/apiClient';
import { AuthContext } from '../../contexts/AuthContext';
import Layout from '../shared/Layout';

export default function UserSettings() {
  const { user } = useContext(AuthContext);
  const [name, setName] = useState(user?.name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [message, setMessage] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      await apiClient.put('/auth/me', { name, phone });
      setMessage('Updated!');
    } catch {
      setMessage('Error updating');
    }
  };

  return (
    <Layout title="Settings">
      {message && <div>{message}</div>}
      <form onSubmit={handleSubmit}>
        <input value={name} onChange={e => setName(e.target.value)} required/>
        <input value={phone} onChange={e => setPhone(e.target.value)} required/>
        <button type="submit">Save</button>
      </form>
    </Layout>
