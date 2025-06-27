import React, {useEffect,useState} from 'react';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';
import adminService from '../../services/adminService';

export default function AdminDashboard(){
  const [stats,setStats] = useState(null);
  useEffect(()=>{adminService.stats().then(res=>setStats(res.data));},[]);
  if(!stats) return <LoadingSpinner />;
  return (
    <Layout title="System Overview">
      <div>Total Users: {stats.total_users}</div>
      <div>Total Brands: {stats.total_brands}</div>
      <div>Total Tickets: {stats.total_tickets}</div>
    </Layout>
  );
}