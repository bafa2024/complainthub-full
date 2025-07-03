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
  const [currentBrand, setCurrentBrand] = useState({ id: null, name: '', support_email: '', industry: '', logo_url: '', contact_info: '' });

  const [deletingId, setDeletingId] = useState(null);
  const [deleteError, setDeleteError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

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
    setCurrentBrand({ id: null, name: '', support_email: '', industry: '', logo_url: '', contact_info: '' });
    setShowForm(true);
  };

  const handleEdit = (brand) => {
    setIsEditing(true);
    setCurrentBrand({
      id: brand.id,
      name: brand.name || '',
      support_email: brand.support_email || '',
      industry: brand.industry || '',
      logo_url: brand.logo_url || '',
      contact_info: brand.contact_info || ''
    });
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
          support_email: currentBrand.support_email,
          industry: currentBrand.industry,
          logo_url: currentBrand.logo_url,
          contact_info: currentBrand.contact_info
        });
      } else {
        await brandService.createBrand({
          name: currentBrand.name,
          support_email: currentBrand.support_email,
          industry: currentBrand.industry,
          logo_url: currentBrand.logo_url,
          contact_info: currentBrand.contact_info
        });
      }
      setShowForm(false);
      setCurrentBrand({ id: null, name: '', support_email: '', industry: '', logo_url: '', contact_info: '' });
      try {
        await fetchBrands(); // Refresh the list
      } catch (fetchErr) {
        console.error('Error refreshing brand list:', fetchErr);
        setError('Brand saved, but failed to refresh list.');
      }
    } catch (err) {
      let backendMsg = '';
      if (err.response && err.response.data && err.response.data.detail) {
        backendMsg = err.response.data.detail;
      } else if (err.message) {
        backendMsg = err.message;
      }
      setError('Failed to save brand. ' + (backendMsg ? 'Details: ' + backendMsg : 'Please check the details.'));
      console.error('Brand save error:', err);
    }
  };

  const handleDelete = async (brandId) => {
    if (!window.confirm('Are you sure you want to delete this brand? This action cannot be undone.')) return;
    setDeletingId(brandId);
    setDeleteError('');
    setSuccessMessage('');
    try {
      await brandService.deleteBrand(brandId);
      await fetchBrands();
      setSuccessMessage('Brand deleted successfully!');
      setError(''); // Clear any previous errors
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      let backendMsg = '';
      if (err.response && err.response.data && err.response.data.detail) {
        backendMsg = err.response.data.detail;
      } else if (err.message) {
        backendMsg = err.message;
      }
      
      // Handle specific error cases
      if (err.response && err.response.status === 400) {
        setDeleteError(backendMsg || 'Cannot delete brand due to associated data.');
      } else if (err.response && err.response.status === 403) {
        setDeleteError('You do not have permission to delete this brand.');
      } else if (err.response && err.response.status === 404) {
        setDeleteError('Brand not found.');
      } else {
        setDeleteError('Failed to delete brand. ' + (backendMsg ? 'Details: ' + backendMsg : 'Please try again.'));
      }
      console.error('Brand delete error:', err);
    } finally {
      setDeletingId(null);
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
      {successMessage && <p className="success-message">{successMessage}</p>}

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
            <div className="form-group">
              <label htmlFor="industry">Industry</label>
              <input type="text" name="industry" id="industry" value={currentBrand.industry} onChange={handleFormChange} />
            </div>
            <div className="form-group">
              <label htmlFor="logo_url">Logo URL</label>
              <input type="text" name="logo_url" id="logo_url" value={currentBrand.logo_url} onChange={handleFormChange} />
            </div>
            <div className="form-group">
              <label htmlFor="contact_info">Contact Info</label>
              <input type="text" name="contact_info" id="contact_info" value={currentBrand.contact_info} onChange={handleFormChange} />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-success">Save Brand</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {deleteError && <p className="error-message">{deleteError}</p>}

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
                <button className="btn-delete" onClick={() => handleDelete(brand.id)} disabled={deletingId === brand.id}>{deletingId === brand.id ? 'Deleting...' : 'Delete'}</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminBrands;