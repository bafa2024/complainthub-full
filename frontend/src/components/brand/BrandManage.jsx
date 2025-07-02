import React, { useEffect, useState, useContext } from 'react';
import brandService from '../../services/brandService';
import LoadingSpinner from '../shared/LoadingSpinner';
import { AuthContext } from '../../contexts/AuthContext';
import Modal from '../shared/Modal';
import { useLocation, useNavigate } from 'react-router-dom';

const BrandManage = () => {
  const { user } = useContext(AuthContext);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewBrand, setViewBrand] = useState(null);
  const [editBrand, setEditBrand] = useState(null);
  const [editLoading, setEditLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const [showAddModal, setShowAddModal] = useState(false);
  const [addBrand, setAddBrand] = useState({ name: '', support_email: user?.email || '', industry: '', logo_url: '' });
  const [addLoading, setAddLoading] = useState(false);
  const [addError, setAddError] = useState('');

  const fetchBrands = async () => {
    try {
      setLoading(true);
      const allBrands = await brandService.getBrands();
      const relatedBrands = allBrands.filter(
        (brand) => brand.support_email && user && brand.support_email.toLowerCase() === user.email.toLowerCase()
      );
      setBrands(relatedBrands);
    } catch (err) {
      setError('Failed to load brands.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user && user.email) {
      fetchBrands();
    }
    // Open add modal if ?add=1 in URL
    if (location.search.includes('add=1')) {
      setShowAddModal(true);
      setAddBrand({ name: '', support_email: user?.email || '', industry: '', logo_url: '' });
    }
    // eslint-disable-next-line
  }, [user, location.search]);

  const handleDelete = async (brandId) => {
    if (!window.confirm('Are you sure you want to delete this brand? This action cannot be undone.')) return;
    setDeleteLoading(true);
    setDeleteError('');
    try {
      await brandService.deleteBrand(brandId);
      await fetchBrands();
    } catch (err) {
      setDeleteError('Failed to delete brand.');
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleEdit = async (e) => {
    e.preventDefault();
    setEditLoading(true);
    setError('');
    try {
      await brandService.updateBrand(editBrand.id, {
        name: editBrand.name,
        support_email: editBrand.support_email,
        industry: editBrand.industry || '',
        logo_url: editBrand.logo_url || ''
      });
      setEditBrand(null);
      await fetchBrands();
    } catch (err) {
      setError('Failed to update brand.');
    } finally {
      setEditLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setAddLoading(true);
    setAddError('');
    try {
      await brandService.createBrand({
        ...addBrand,
        support_email: user.email // Always set to current user's email
      });
      setShowAddModal(false);
      setAddBrand({ name: '', support_email: user.email, industry: '', logo_url: '' });
      await fetchBrands();
      navigate('/brand/manage-brands'); // Remove ?add=1 from URL
    } catch (err) {
      setAddError('Failed to add brand.');
    } finally {
      setAddLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="container mt-4">
      <h1>Manage Brands</h1>
      <button className="btn btn-success mb-3" onClick={() => setShowAddModal(true)}>
        + Add Brand
      </button>
      {error && <div className="alert alert-danger">{error}</div>}
      {deleteError && <div className="alert alert-danger">{deleteError}</div>}
      {brands.length === 0 ? (
        <div className="alert alert-info">No brands found for your email.</div>
      ) : (
        <table className="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Support Email</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {brands.map((brand) => (
              <tr key={brand.id}>
                <td>{brand.id}</td>
                <td>{brand.name}</td>
                <td>{brand.support_email}</td>
                <td>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn btn-sm btn-info" onClick={() => setViewBrand(brand)}>View</button>
                    <button className="btn btn-sm btn-warning" onClick={() => setEditBrand(brand)}>Edit</button>
                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(brand.id)} disabled={deleteLoading}>{deleteLoading ? 'Deleting...' : 'Delete'}</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* View Modal */}
      {viewBrand && (
        <Modal onClose={() => setViewBrand(null)} title="Brand Details">
          <p><strong>ID:</strong> {viewBrand.id}</p>
          <p><strong>Name:</strong> {viewBrand.name}</p>
          <p><strong>Support Email:</strong> {viewBrand.support_email}</p>
          <button className="btn btn-secondary" onClick={() => setViewBrand(null)}>Close</button>
        </Modal>
      )}

      {/* Edit Modal */}
      {editBrand && (
        <Modal onClose={() => setEditBrand(null)} title="Edit Brand">
          <form onSubmit={handleEdit}>
            <div className="mb-3">
              <label className="form-label">Name</label>
              <input type="text" className="form-control" value={editBrand.name} onChange={e => setEditBrand({ ...editBrand, name: e.target.value })} required />
            </div>
            <div className="mb-3">
              <label className="form-label">Support Email</label>
              <input type="email" className="form-control" value={editBrand.support_email} onChange={e => setEditBrand({ ...editBrand, support_email: e.target.value })} required />
            </div>
            <div className="mb-3">
              <label className="form-label">Industry</label>
              <input type="text" className="form-control" value={editBrand.industry || ''} onChange={e => setEditBrand({ ...editBrand, industry: e.target.value })} />
            </div>
            <div className="mb-3">
              <label className="form-label">Logo URL</label>
              <input type="text" className="form-control" value={editBrand.logo_url || ''} onChange={e => setEditBrand({ ...editBrand, logo_url: e.target.value })} />
            </div>
            <button className="btn btn-primary" type="submit" disabled={editLoading}>{editLoading ? 'Saving...' : 'Save'}</button>
            <button className="btn btn-secondary ms-2" type="button" onClick={() => setEditBrand(null)}>Cancel</button>
          </form>
        </Modal>
      )}

      {/* Add Brand Modal */}
      {showAddModal && (
        <Modal onClose={() => { setShowAddModal(false); navigate('/brand/manage-brands'); }} title="Add Brand">
          <form onSubmit={handleAdd}>
            <div className="mb-3">
              <label className="form-label">Name</label>
              <input type="text" className="form-control" value={addBrand.name} onChange={e => setAddBrand({ ...addBrand, name: e.target.value })} required />
            </div>
            <div className="mb-3">
              <label className="form-label">Support Email</label>
              <input type="email" className="form-control" value={addBrand.support_email} disabled />
            </div>
            <div className="mb-3">
              <label className="form-label">Industry</label>
              <input type="text" className="form-control" value={addBrand.industry} onChange={e => setAddBrand({ ...addBrand, industry: e.target.value })} />
            </div>
            <div className="mb-3">
              <label className="form-label">Logo URL</label>
              <input type="text" className="form-control" value={addBrand.logo_url} onChange={e => setAddBrand({ ...addBrand, logo_url: e.target.value })} />
            </div>
            {addError && <div className="alert alert-danger">{addError}</div>}
            <button className="btn btn-primary" type="submit" disabled={addLoading}>{addLoading ? 'Adding...' : 'Add Brand'}</button>
            <button className="btn btn-secondary ms-2" type="button" onClick={() => { setShowAddModal(false); navigate('/brand/manage-brands'); }}>Cancel</button>
          </form>
        </Modal>
      )}
    </div>
  );
};

export default BrandManage; 