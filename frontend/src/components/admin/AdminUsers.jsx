import React, {useEffect,useState} from 'react';
import Layout from '../shared/Layout';
import LoadingSpinner from '../shared/LoadingSpinner';
import adminService from '../../services/adminService';

export default function AdminUsers(){
  const [users,setUsers] = useState(null);
  useEffect(()=>{adminService.users().then(res=>setUsers(res.data));},[]);
  if(!users) return <LoadingSpinner />;
  return (
    <Layout title="User Management">
      <ul>{users.map(u=><li key={u.id}>{u.name} ({u.email})</li>)}</ul>
    </Layout>
  );
}