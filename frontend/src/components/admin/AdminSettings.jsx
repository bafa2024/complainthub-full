import React, {useEffect,useState} from 'react';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';
import adminService from '../../services/adminService';

export default function AdminSettings(){
  const [settings,setSettings] = useState(null);
  useEffect(()=>{adminService.settings().then(res=>setSettings(res.data));},[]);
  if(!settings) return <LoadingSpinner />;
  return (
    <Layout title="Settings">
      <pre>{JSON.stringify(settings,null,2)}</pre>
    </Layout>
  );
}