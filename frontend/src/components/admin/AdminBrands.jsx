import React, { useState, useEffect } from 'react';
import adminService from '../../services/adminService';
import brandService from '../../services/brandService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './Admin.css'; // Uses the existing Admin stylesheet

const AdminBrands = () => {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // State for the create/edit form
  const [showForm, setShowForm] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentBrand, setCurrentBrand] = useState({ id: null, name: '', support_email: '' });

  const fetchBrands = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAllBrands();
      setBrands(data);
    } catch (err) {
      setError('Could not load brands.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBrands();
  }, []);

  const handleCreateNew = () => {
    setIsEditing(false);
    setCurrentBrand({ id: null, name: '', support_email: '' });
    setShowForm(true);
  };

  const handleEdit = (brand) => {
    setIsEditing(true);
    setCurrentBrand(brand);
    setShowForm(true);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setCurrentBrand(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isEditing) {
        await brandService.updateBrand(currentBrand.id, { 
            name: currentBrand.name, 
            support_email: currentBrand.support_email 
        });
      } else {
        await brandService.createBrand({ 
            name: currentBrand.name, 
            support_email: currentBrand.support_email 
        });
      }
      setShowForm(false);
      fetchBrands(); // Refresh the list
    } catch (err) {
      setError('Failed to save brand. Please check the details.');
      console.error(err);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Manage Brands</h1>
        <button className="btn btn-primary" onClick={handleCreateNew}>+ Add New Brand</button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {showForm && (
        <div className="admin-form-container">
          <form onSubmit={handleSubmit}>
            <h3>{isEditing ? 'Edit Brand' : 'Create New Brand'}</h3>
            <div className="form-group">
              <label htmlFor="name">Brand Name</label>
              <input type="text" name="name" id="name" value={currentBrand.name} onChange={handleFormChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="support_email">Support Email</label>
              <input type="email" name="support_email" id="support_email" value={currentBrand.support_email} onChange={handleFormChange} required />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-success">Save Brand</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Support Email</th>
            <th>Credits</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {brands.map(brand => (
            <tr key={brand.id}>
              <td>{brand.id}</td>
              <td>{brand.name}</td>
              <td>{brand.support_email}</td>
              <td>{brand.credit_balance}</td>
              <td>
                <button className="btn-edit" onClick={() => handleEdit(brand)}>Edit</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminBrands;