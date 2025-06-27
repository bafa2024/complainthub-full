import React, {useEffect,useState} from 'react';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';
import ticketService from '../../services/ticketService';

export default function BrandDashboard(){
  const [stats, setStats] = useState(null);
  useEffect(()=>{ticketService.stats().then(res=>setStats(res.data));},[]);
  if(!stats) return <LoadingSpinner />;
  return (
    <Layout title="Dashboard">
      <div>Total: {stats.total}</div>
      <div>Open: {stats.open}</div>
      <div>Resolved: {stats.resolved}</div>
      <div>Avg Hrs: {stats.avg_resolution_hours.toFixed(2)}</div>
    </Layout>
  );
}
