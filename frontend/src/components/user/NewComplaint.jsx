import React, { useState } from 'react';
import ticketService from '../../services/ticketService';
import { useNavigate } from 'react-router-dom';
import Layout from '../shared/Layout';

export default function NewComplaint() {
  const [desc, setDesc] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const ticket = await ticketService.create({ description: desc });
      navigate(`/user/ticket/${ticket.id}`);
    } catch {
      setError('Could not create ticket');
    }
  };

  return (
    <Layout title="New Complaint">
      {error && <div style={{color:'red'}}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <textarea value={desc} onChange={e => setDesc(e.target.value)} required/>
        <button type="submit">Submit</button>
      </form>
    </Layout>
