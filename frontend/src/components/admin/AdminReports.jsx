import React, {useEffect,useState} from 'react';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';
import adminService from '../../services/adminService';

export default function AdminReports(){
  const [reports,setReports] = useState(null);
  useEffect(()=>{adminService.reports().then(res=>setReports(res.data));},[]);
  if(!reports) return <LoadingSpinner />;
  return (
    <Layout title="System Reports">
      <p>No reports available</p>
    </Layout>
  );
}