import React, {useState, useContext} from 'react';
import authService from '../../services/authService';
import {AuthContext} from '../../contexts/AuthContext';
import {useNavigate} from 'react-router-dom';

export default function BrandLogin(){
  const navigate = useNavigate();
  const {setToken} = useContext(AuthContext);
  const [form, setForm] = useState({email:'',password:''}); 
  const [error,setError] = useState('');

  const handleChange=e=>setForm({...form,[e.target.name]:e.target.value});
  const submit=async e=>{
    e.preventDefault();
    try{
      const res = await authService.login(form);
      setToken(res.data.access_token);
      navigate('/admin/dashboard');
    }catch{
      setError('Login failed');
    }
  };

  return (
    <form onSubmit={submit}>
      <h2>Admin Login</h2>
      {error && <div style={{color:'red'}}>{error}</div>}
      <input name="email" type="email" placeholder="Email" onChange={handleChange} required/>
      <input name="password" type="password" placeholder="Password" onChange={handleChange} required/>
      <button type="submit">Log In</button>
    </form>
  );
}