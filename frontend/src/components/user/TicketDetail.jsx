import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';

export default function TicketDetail() {
  const { id } = useParams();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ticketService.get(id)
      .then(data => setTicket(data))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <Layout title={`Ticket #${id}`}>
      {loading && <LoadingSpinner />}
      {ticket && (
        <>
          <p><strong>Description:</strong> {ticket.description}</p>
          <p><strong>Status:</strong> {ticket.status}</p>
        </>
      )}
    </Layout>
