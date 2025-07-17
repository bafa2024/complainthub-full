import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import adminService from '../../services/adminService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './Admin.css';

const AdminComplaintDetail = () => {
  const { complaintId } = useParams();
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchComplaint();
  }, [complaintId]);

  const fetchComplaint = async () => {
    try {
      setLoading(true);
      setError('');
      const complaintData = await ticketService.getTicketById(complaintId);
      setComplaint(complaintData);
    } catch (err) {
      console.error('Error fetching complaint:', err);
      setError('Failed to load complaint details: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    try {
      setUpdating(true);
      await ticketService.updateTicket(complaintId, { status: newStatus });
      // Refresh the complaint data
      await fetchComplaint();
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Failed to update status: ' + (err.message || 'Unknown error'));
    } finally {
      setUpdating(false);
    }
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="admin-container">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-container">
        <div className="alert alert-danger">
          <h5>Error Loading Complaint</h5>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchComplaint}>Retry</button>
        </div>
      </div>
    );
  }

  if (!complaint) {
    return (
      <div className="admin-container">
        <div className="alert alert-warning">
          <h5>Complaint Not Found</h5>
          <p>The requested complaint could not be found.</p>
          <Link to="/admin/complaints" className="btn btn-primary">Back to Complaints</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <Link to="/admin/complaints" className="btn btn-outline-secondary btn-sm">
            &larr; Back to Complaints
          </Link>
          <h1 className="mt-2 mb-0">Complaint #{complaint.id}</h1>
        </div>
        <div className="d-flex gap-2">
          <button 
            className="btn btn-outline-primary btn-sm" 
            onClick={fetchComplaint}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="row">
        {/* Complaint Details */}
        <div className="col-lg-8">
          <div className="card mb-4">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Complaint Details</h5>
              <span className={`badge ${getStatusBadgeClass(complaint.status)} fs-6`}>
                {complaint.status}
              </span>
            </div>
            <div className="card-body">
              <h4 className="card-title">{complaint.title}</h4>
              <p className="card-text">{complaint.description || 'No description provided.'}</p>
              
              <div className="row mt-4">
                <div className="col-md-6">
                  <h6>Complaint Information</h6>
                  <table className="table table-sm">
                    <tbody>
                      <tr>
                        <td><strong>ID:</strong></td>
                        <td>#{complaint.id}</td>
                      </tr>
                      <tr>
                        <td><strong>Created:</strong></td>
                        <td>{formatDate(complaint.created_at)}</td>
                      </tr>
                      <tr>
                        <td><strong>Updated:</strong></td>
                        <td>{formatDate(complaint.updated_at)}</td>
                      </tr>
                      <tr>
                        <td><strong>Priority:</strong></td>
                        <td>
                          <span className={`badge ${complaint.priority === 'high' ? 'badge-danger' : complaint.priority === 'medium' ? 'badge-warning' : 'badge-info'}`}>
                            {complaint.priority || 'normal'}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                
                <div className="col-md-6">
                  <h6>Status Management</h6>
                  <div className="d-grid gap-2">
                    <button 
                      className={`btn btn-sm ${complaint.status === 'new' ? 'btn-primary' : 'btn-outline-primary'}`}
                      onClick={() => handleStatusUpdate('new')}
                      disabled={updating || complaint.status === 'new'}
                    >
                      Mark as New
                    </button>
                    <button 
                      className={`btn btn-sm ${complaint.status === 'in-progress' ? 'btn-warning' : 'btn-outline-warning'}`}
                      onClick={() => handleStatusUpdate('in-progress')}
                      disabled={updating || complaint.status === 'in-progress'}
                    >
                      Mark In Progress
                    </button>
                    <button 
                      className={`btn btn-sm ${complaint.status === 'resolved' ? 'btn-success' : 'btn-outline-success'}`}
                      onClick={() => handleStatusUpdate('resolved')}
                      disabled={updating || complaint.status === 'resolved'}
                    >
                      Mark Resolved
                    </button>
                    <button 
                      className={`btn btn-sm ${complaint.status === 'closed' ? 'btn-secondary' : 'btn-outline-secondary'}`}
                      onClick={() => handleStatusUpdate('closed')}
                      disabled={updating || complaint.status === 'closed'}
                    >
                      Mark Closed
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="col-lg-4">
          {/* Customer Information */}
          <div className="card mb-4">
            <div className="card-header">
              <h6 className="mb-0">Customer Information</h6>
            </div>
            <div className="card-body">
              {complaint.owner ? (
                <div>
                  <p><strong>Name:</strong> {complaint.owner.full_name || 'N/A'}</p>
                  <p><strong>Email:</strong> {complaint.owner.email || 'N/A'}</p>
                  <p><strong>Phone:</strong> {complaint.owner.phone || 'N/A'}</p>
                  <p><strong>User ID:</strong> #{complaint.owner.id}</p>
                </div>
              ) : (
                <p className="text-muted">Customer information not available</p>
              )}
            </div>
          </div>

          {/* Brand Information */}
          <div className="card mb-4">
            <div className="card-header">
              <h6 className="mb-0">Brand Information</h6>
            </div>
            <div className="card-body">
              {complaint.brand ? (
                <div>
                  <p><strong>Brand:</strong> {complaint.brand.name}</p>
                  <p><strong>Brand ID:</strong> #{complaint.brand.id}</p>
                  <p><strong>Email:</strong> {complaint.brand.email || 'N/A'}</p>
                  <Link 
                    to={`/admin/brands`} 
                    className="btn btn-sm btn-outline-primary"
                  >
                    View Brand Details
                  </Link>
                </div>
              ) : (
                <p className="text-muted">Brand information not available</p>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Quick Actions</h6>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <Link 
                  to={`/brand/tickets/${complaint.id}`} 
                  className="btn btn-sm btn-outline-secondary"
                >
                  View as Brand
                </Link>
                <Link 
                  to={`/tickets/${complaint.id}`} 
                  className="btn btn-sm btn-outline-info"
                >
                  View as Customer
                </Link>
                <button 
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to delete this complaint? This action cannot be undone.')) {
                      // Handle deletion
                      alert('Delete functionality not implemented yet');
                    }
                  }}
                >
                  Delete Complaint
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminComplaintDetail; 