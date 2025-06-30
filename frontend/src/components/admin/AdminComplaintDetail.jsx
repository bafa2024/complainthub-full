import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import brandService from '../../services/brandService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './Admin.css';

const AdminComplaintDetail = () => {
  const { complaintId } = useParams();
  const navigate = useNavigate();
  const [complaint, setComplaint] = useState(null);
  const [brand, setBrand] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchComplaintDetails();
  }, [complaintId]);

  const fetchComplaintDetails = async () => {
    try {
      setLoading(true);
      setError('');
      
      const complaintData = await ticketService.getTicketById(complaintId);
      setComplaint(complaintData);
      
      if (complaintData.brand_id) {
        const brandData = await brandService.getBrandById(complaintData.brand_id);
        setBrand(brandData);
      }
    } catch (err) {
      console.error('Error fetching complaint details:', err);
      setError('Failed to load complaint details: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    try {
      setUpdating(true);
      await ticketService.updateTicket(complaintId, { status: newStatus });
      await fetchComplaintDetails(); // Refresh the data
    } catch (err) {
      console.error('Error updating status:', err);
      setError('Failed to update status: ' + (err.message || 'Unknown error'));
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
        <h1 className="mb-4">Complaint Details</h1>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-container">
        <h1 className="mb-4">Complaint Details</h1>
        <div className="alert alert-danger">
          <h5>Error Loading Complaint</h5>
          <p>{error}</p>
          <button className="btn btn-primary me-2" onClick={fetchComplaintDetails}>Retry</button>
          <button className="btn btn-secondary" onClick={() => navigate('/admin/complaints')}>Back to List</button>
        </div>
      </div>
    );
  }

  if (!complaint) {
    return (
      <div className="admin-container">
        <h1 className="mb-4">Complaint Details</h1>
        <div className="alert alert-warning">
          <h5>Complaint Not Found</h5>
          <p>The requested complaint could not be found.</p>
          <button className="btn btn-secondary" onClick={() => navigate('/admin/complaints')}>Back to List</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Complaint #{complaint.id}</h1>
        <div>
          <button 
            className="btn btn-outline-secondary me-2" 
            onClick={() => navigate('/admin/complaints')}
          >
            Back to List
          </button>
          <Link 
            to={`/brand/tickets/${complaint.id}`} 
            className="btn btn-outline-primary"
          >
            Brand View
          </Link>
        </div>
      </div>

      <div className="row">
        <div className="col-lg-8">
          {/* Complaint Details */}
          <div className="card mb-4">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5>Complaint Details</h5>
              <span className={`badge ${getStatusBadgeClass(complaint.status)} fs-6`}>
                {complaint.status}
              </span>
            </div>
            <div className="card-body">
              <h4>{complaint.title}</h4>
              <p className="text-muted mb-3">
                Created on {formatDate(complaint.created_at)}
                {complaint.updated_at && complaint.updated_at !== complaint.created_at && 
                  <span> • Updated on {formatDate(complaint.updated_at)}</span>
                }
              </p>
              
              <div className="mb-4">
                <h6>Description:</h6>
                <p className="border rounded p-3 bg-light">
                  {complaint.description || 'No description provided'}
                </p>
              </div>

              {complaint.transcript && (
                <div className="mb-4">
                  <h6>Voice Transcript:</h6>
                  <p className="border rounded p-3 bg-light">
                    {complaint.transcript}
                  </p>
                </div>
              )}

              {complaint.voice_recording_url && (
                <div className="mb-4">
                  <h6>Voice Recording:</h6>
                  <audio controls className="w-100">
                    <source src={complaint.voice_recording_url} type="audio/webm" />
                    Your browser does not support the audio element.
                  </audio>
                </div>
              )}

              {/* Status Update */}
              <div className="mb-4">
                <h6>Update Status:</h6>
                <div className="btn-group" role="group">
                  <button 
                    type="button" 
                    className={`btn btn-sm ${complaint.status === 'new' ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => handleStatusUpdate('new')}
                    disabled={updating}
                  >
                    New
                  </button>
                  <button 
                    type="button" 
                    className={`btn btn-sm ${complaint.status === 'in-progress' ? 'btn-warning' : 'btn-outline-warning'}`}
                    onClick={() => handleStatusUpdate('in-progress')}
                    disabled={updating}
                  >
                    In Progress
                  </button>
                  <button 
                    type="button" 
                    className={`btn btn-sm ${complaint.status === 'resolved' ? 'btn-success' : 'btn-outline-success'}`}
                    onClick={() => handleStatusUpdate('resolved')}
                    disabled={updating}
                  >
                    Resolved
                  </button>
                  <button 
                    type="button" 
                    className={`btn btn-sm ${complaint.status === 'closed' ? 'btn-secondary' : 'btn-outline-secondary'}`}
                    onClick={() => handleStatusUpdate('closed')}
                    disabled={updating}
                  >
                    Closed
                  </button>
                </div>
                {updating && <small className="text-muted ms-2">Updating...</small>}
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          {/* Customer Information */}
          <div className="card mb-4">
            <div className="card-header">
              <h5>Customer Information</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <strong>Name:</strong><br />
                {complaint.owner?.full_name || 'Not provided'}
              </div>
              <div className="mb-3">
                <strong>Email:</strong><br />
                {complaint.owner?.email || 'Not provided'}
              </div>
              <div className="mb-3">
                <strong>Phone:</strong><br />
                {complaint.owner?.phone_number || 'Not provided'}
              </div>
              <div className="mb-3">
                <strong>Channel:</strong><br />
                <span className="badge bg-info">{complaint.channel || 'web'}</span>
              </div>
            </div>
          </div>

          {/* Brand Information */}
          <div className="card mb-4">
            <div className="card-header">
              <h5>Brand Information</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <strong>Brand:</strong><br />
                {brand?.name || 'Unknown Brand'}
              </div>
              <div className="mb-3">
                <strong>Support Email:</strong><br />
                {brand?.support_email || 'Not provided'}
              </div>
              <div className="mb-3">
                <strong>Industry:</strong><br />
                {brand?.industry || 'Not specified'}
              </div>
            </div>
          </div>

          {/* Additional Information */}
          <div className="card">
            <div className="card-header">
              <h5>Additional Information</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <strong>Category:</strong><br />
                <span className="badge bg-secondary">{complaint.category || 'complaint'}</span>
              </div>
              <div className="mb-3">
                <strong>Urgency:</strong><br />
                <span className="badge bg-danger">{complaint.urgency || '1'}</span>
              </div>
              {complaint.satisfaction_rating && (
                <div className="mb-3">
                  <strong>Satisfaction Rating:</strong><br />
                  <div className="d-flex align-items-center">
                    {[...Array(5)].map((_, i) => (
                      <span key={i} className={`fs-5 ${i < complaint.satisfaction_rating ? 'text-warning' : 'text-muted'}`}>
                        ★
                      </span>
                    ))}
                    <span className="ms-2">({complaint.satisfaction_rating}/5)</span>
                  </div>
                </div>
              )}
              {complaint.is_public && (
                <div className="mb-3">
                  <strong>Public Complaint:</strong><br />
                  <span className="badge bg-warning">Yes</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminComplaintDetail; 