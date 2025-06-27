import React, {useEffect,useState} from 'react';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';
import ticketService from '../../services/ticketService';
import TicketCard from '../shared/TicketCard';

export default function BrandTickets(){
  const [tickets, setTickets] = useState(null);
  useEffect(()=>{ticketService.list().then(res=>setTickets(res.data));},[]);
  if(!tickets) return <LoadingSpinner />;
  return (
    <Layout title="Tickets">
      {tickets.map(t => <TicketCard key={t.id} ticket={t} />)}
    </Layout>
  );
}
