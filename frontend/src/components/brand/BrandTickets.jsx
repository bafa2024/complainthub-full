import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import LoadingSpinner from '../shared/LoadingSpinner';
import ticketService from '../../services/ticketService';
import TicketCard from '../shared/TicketCard';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

export default function BrandTickets() {
  const [tickets, setTickets] = useState(null);
  const query = useQuery();
  const statusFilter = query.get('status');

  useEffect(() => {
    ticketService.getTickets().then(res => setTickets(res));
  }, []);

  if (!tickets) return <LoadingSpinner />;

  let filteredTickets = tickets;
  let heading = 'All Complaints';
  if (statusFilter) {
    filteredTickets = tickets.filter(t => t.status === statusFilter);
    if (statusFilter === 'new') heading = 'New Complaints';
    else if (statusFilter === 'in-progress') heading = 'In Progress';
    else if (statusFilter === 'resolved') heading = 'Resolved';
  }

  return (
    <div className="container-fluid">
      <h1 className="mb-4">{heading}</h1>
      {filteredTickets.length > 0 ? (
        <div className="row g-3">
          {filteredTickets.map(t => (
            <div key={t.id} className="col-12">
              <TicketCard ticket={t} linkPrefix="/brand/tickets" />
            </div>
          ))}
        </div>
      ) : (
        <div className="card card-body text-center">No tickets found for this status.</div>
      )}
    </div>
  );
}
