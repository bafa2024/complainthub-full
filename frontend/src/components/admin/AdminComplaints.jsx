import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import adminService from '../../services/adminService';
import ticketService from '../../services/ticketService';
import brandService from '../../services/brandService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './Admin.css';

const AdminComplaints = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [complaints, setComplaints] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filter states
  const [selectedBrand, setSelectedBrand] = useState(searchParams.get('brand') || '');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Fetch complaints and brands concurrently
      const [complaintsData, brandsData] = await Promise.all([
        ticketService.getTickets(),
        brandService.getBrands()
      ]);

      setComplaints(complaintsData);
      setBrands(brandsData);
    } catch (err) {
      console.error('Error fetching complaints data:', err);
      setError('Failed to load complaints data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  // Filter complaints based on selected criteria
  const filteredComplaints = complaints.filter(complaint => {
    // Brand filter
    if (selectedBrand && complaint.brand_id !== parseInt(selectedBrand)) {
      return false;
    }
    
    // Status filter
    if (statusFilter && complaint.status !== statusFilter) {
      return false;
    }
    
    // Search term filter (search in title, description, and customer name)
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const titleMatch = complaint.title?.toLowerCase().includes(searchLower);
      const descriptionMatch = complaint.description?.toLowerCase().includes(searchLower);
      const customerMatch = complaint.owner?.full_name?.toLowerCase().includes(searchLower);
      const brandMatch = complaint.brand?.name?.toLowerCase().includes(searchLower);
      
      if (!titleMatch && !descriptionMatch && !customerMatch && !brandMatch) {
        return false;
      }
    }
    
    // Date filter
    if (dateFilter) {
      const complaintDate = new Date(complaint.created_at).toDateString();
      const filterDate = new Date(dateFilter).toDateString();
      if (complaintDate !== filterDate) {
        return false;
      }
    }
    
    return true;
  });

  const getBrandName = (brandId) => {
    const brand = brands.find(b => b.id === brandId);
    return brand ? brand.name : 'Unknown Brand';
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'new': return 'badge-primary';
      case 'in-progress': return 'badge-warning';
      case 'resolved': return 'badge-success';
      case 'closed': return 'badge-secondary';
      default: return 'badge-light';
    }
  };

  const handleBrandChange = (e) => {
    const brandId = e.target.value;
    setSelectedBrand(brandId);
    
    // Update URL parameters
    if (brandId) {
      setSearchParams({ brand: brandId });
    } else {
      setSearchParams({});
    }
  };

  const handleStatusChange = (e) => {
    setStatusFilter(e.target.value);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleDateChange = (e) => {
    setDateFilter(e.target.value);
  };

  const clearFilters = () => {
    setSelectedBrand('');
    setStatusFilter('');
    setSearchTerm('');
    setDateFilter('');
  };

  if (loading) {
    return (
      <div className="admin-container">
        <h1 className="mb-4">Manage Complaints</h1>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Manage Complaints</h1>
        <button 
          className="btn btn-outline-primary btn-sm" 
          onClick={fetchData}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      {error && (
        <div className="alert alert-danger mb-4">
          <h5>Error Loading Complaints</h5>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchData}>Retry</button>
        </div>
      )}

      {/* Filters Section */}
      <div className="card mb-4">
        <div className="card-header">
          <h5>Filters & Search</h5>
        </div>
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-3">
              <label htmlFor="brandFilter" className="form-label">Brand</label>
              <select 
                id="brandFilter" 
                className="form-select" 
                value={selectedBrand} 
                onChange={handleBrandChange}
              >
                <option value="">All Brands</option>
                {brands.map(brand => (
                  <option key={brand.id} value={brand.id}>
                    {brand.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="col-md-3">
              <label htmlFor="statusFilter" className="form-label">Status</label>
              <select 
                id="statusFilter" 
                className="form-select" 
                value={statusFilter} 
                onChange={handleStatusChange}
              >
                <option value="">All Statuses</option>
                <option value="new">New</option>
                <option value="in-progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
              </select>
            </div>
            
            <div className="col-md-3">
              <label htmlFor="dateFilter" className="form-label">Date</label>
              <input 
                type="date" 
                id="dateFilter" 
                className="form-control" 
                value={dateFilter} 
                onChange={handleDateChange}
              />
            </div>
            
            <div className="col-md-3">
              <label htmlFor="searchFilter" className="form-label">Search</label>
              <input 
                type="text" 
                id="searchFilter" 
                className="form-control" 
                placeholder="Search complaints..." 
                value={searchTerm} 
                onChange={handleSearchChange}
              />
            </div>
          </div>
          
          <div className="mt-3">
            <button 
              className="btn btn-secondary btn-sm" 
              onClick={clearFilters}
            >
              Clear Filters
            </button>
            <span className="ms-3 text-muted">
              Showing {filteredComplaints.length} of {complaints.length} complaints
            </span>
          </div>
        </div>
      </div>

      {/* Complaints Table */}
      <div className="card">
        <div className="card-header">
          <h5>All Complaints</h5>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Brand</th>
                  <th>Customer</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredComplaints.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center text-muted py-4">
                      {complaints.length === 0 ? 'No complaints found' : 'No complaints match the current filters'}
                    </td>
                  </tr>
                ) : (
                  filteredComplaints.map(complaint => (
                    <tr key={complaint.id}>
                      <td>#{complaint.id}</td>
                      <td>
                        <div className="fw-bold">{complaint.title}</div>
                        <small className="text-muted">
                          {complaint.description?.substring(0, 50)}...
                        </small>
                      </td>
                      <td>
                        <span className="badge bg-info">
                          {getBrandName(complaint.brand_id)}
                        </span>
                      </td>
                      <td>
                        {complaint.owner?.full_name || 'Unknown'}
                        <br />
                        <small className="text-muted">
                          {complaint.owner?.email}
                        </small>
                      </td>
                      <td>
                        <span className={`badge ${getStatusBadgeClass(complaint.status)}`}>
                          {complaint.status}
                        </span>
                      </td>
                      <td>
                        {new Date(complaint.created_at).toLocaleDateString()}
                        <br />
                        <small className="text-muted">
                          {new Date(complaint.created_at).toLocaleTimeString()}
                        </small>
                      </td>
                      <td>
                        <Link 
                          to={`/admin/complaints/${complaint.id}`} 
                          className="btn btn-sm btn-primary me-1"
                        >
                          View
                        </Link>
                        <Link 
                          to={`/brand/tickets/${complaint.id}`} 
                          className="btn btn-sm btn-outline-secondary"
                        >
                          Brand View
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminComplaints; 