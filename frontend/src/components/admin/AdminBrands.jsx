import React, {useEffect,useState} from 'react';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';
import adminService from '../../services/adminService';

export default function AdminBrands(){
  const [brands,setBrands] = useState(null);
  useEffect(()=>{adminService.brands().then(res=>setBrands(res.data));},[]);
  if(!brands) return <LoadingSpinner />;
  return (
    <Layout title="Brands Management">
      <ul>{brands.map(b=><li key={b.id}>{b.name} ({b.email})</li>)}</ul>
    </Layout>
  );
}