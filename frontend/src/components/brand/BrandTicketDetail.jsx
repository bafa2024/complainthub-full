import React, {useEffect,useState} from 'react';
import {useParams} from 'react-router-dom';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';
import ticketService from '../../services/ticketService';

export default function BrandTicketDetail(){
  const {id}=useParams(); const [t, setT] = useState(null);
  useEffect(()=>{ticketService.list().then(res=>setT(res.data.find(x=>x.id==id)));},[]);
  if(!t) return <LoadingSpinner />;
  return (
    <Layout title={\`Ticket #\${id}\`}>
      <p>{t.description}</p>
      <p>Status: {t.status}</p>
      <p>Assigned: {t.assigned_to || '---'}</p>
    </Layout>
  );
}
