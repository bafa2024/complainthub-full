import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import { useAuth } from '../../contexts/AuthContext';
import './BrandDashboard.css';

// SVG Icons for cards
const TicketIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" className="bi bi-ticket-detailed-fill" viewBox="0 0 16 16"><path d="M0 4.5A1.5 1.5 0 0 1 1.5 3h13A1.5 1.5 0 0 1 16 4.5V6a.5.5 0 0 1-.5.5 1.5 1.5 0 0 0 0 3 .5.5 0 0 1 .5.5v1.5a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 11.5V10a.5.5 0 0 1 .5-.5 1.5 1.5 0 1 0 0-3A.5.5 0 0 1 0 6zM4 5.5a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 0-1h-7a.5.5 0 0 0-.5.5m0 2a.5.5 0 0 0 .5.5h7a.5.5 0 0 0 0-1h-7a.5.5 0 0 0-.5.5m0 2a.5.5 0 0 0 .5.5h4a.5.5 0 0 0 0-1h-4a.5.5 0 0 0-.5.5"/></svg>;
const ClockIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" className="bi bi-clock-history" viewBox="0 0 16 16"><path d="M8.515 1.019A7 7 0 0 0 8 1V0a8 8 0 0 1 .589.022zm2.004.45a7 7 0 0 0-.985-.299l.219-.976q.576.129 1.126.342zM13.5 2.344a7 7 0 0 0-.942-.815l.404-.922a8 8 0 0 1 1.125.99zM11.5 15a6.5 6.5 0 1 1-11.85-4.5H.15a.5.5 0 0 1 0-1h.434a6.5 6.5 0 0 1 11.85 4.5z"/><path d="M8.5 5.5a.5.5 0 0 0-1 0v3.362l-1.429 2.38a.5.5 0 1 0 .858.515l1.5-2.5A.5.5 0 0 0 8.5 9z"/></svg>;
const CheckIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" className="bi bi-patch-check-fill" viewBox="0 0 16 16"><path d="M10.067.87a2.89 2.89 0 0 0-4.134 0l-.622.638-.89-.011a2.89 2.89 0 0 0-2.924 2.924l.01.89-.636.622a2.89 2.89 0 0 0 0 4.134l.637.622-.011.89a2.89 2.89 0 0 0 2.924 2.924l.89-.01.622.636a2.89 2.89 0 0 0 4.134 0l.622-.637.89.011a2.89 2.89 0 0 0 2.924-2.924l-.01-.89.636-.622a2.89 2.89 0 0 0 0-4.134l-.637-.622.011-.89a2.89 2.89 0 0 0-2.924-2.924l-.89.01zm.287 5.984-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7 8.793l2.646-2.647a.5.5 0 0 1 .708.708"/></svg>;
const CreditIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" className="bi bi-wallet-fill" viewBox="0 0 16 16"><path d="M1.5 2A1.5 1.5 0 0 0 0 3.5v2h6a.5.5 0 0 1 .5.5c0 .253.08.644.306.958.207.288.557.542 1.194.542s.987-.254 1.194-.542C9.42 6.644 9.5 6.253 9.5 6a.5.5 0 0 1 .5-.5h6v-2A1.5 1.5 0 0 0 14.5 2z"/><path d="M16 6.5h-5.551a2.7 2.7 0 0 1-.443 1.042C9.613 8.088 8.963 8.5 8 8.5s-1.613-.412-2.006-.958A2.7 2.7 0 0 1 5.551 6.5H0v6A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5z"/></svg>;

const BrandDashboard = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth(); // Get brand user info

  useEffect(() => {
    const fetchBrandTickets = async () => {
      try {
        setLoading(true);
        const allTickets = await ticketService.getTickets(); 
        // Backend already filters tickets by brand for brand users
        setTickets(allTickets);
      } catch (err) {
        setError('Failed to load tickets for your brand.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchBrandTickets();
  }, []);

  const getStatusCounts = () => {
    const counts = { new: 0, "in-progress": 0, resolved: 0 };
    tickets.forEach(ticket => {
      if (ticket.status in counts) {
        counts[ticket.status]++;
      }
    });
    return counts;
  };

  const statusCounts = getStatusCounts();

  if (loading) return <LoadingSpinner />;

  return (
    <div className="brand-dashboard-container">
      <h1 className="mb-4">Brand Dashboard</h1>
      {error && <div className="alert alert-danger">{error}</div>}

      <div className="alert alert-info text-center mb-4">
        <strong>Total Complaints for Your Brand: {tickets.length}</strong>
      </div>

      <div className="stats-grid">
        <div className="stat-card-brand">
          <div className="stat-content">
            <div className="stat-icon new-complaints">
              <TicketIcon />
            </div>
            <div className="stat-info">
              <h6>New Complaints</h6>
              <h2>{statusCounts.new}</h2>
            </div>
          </div>
        </div>
        
        <div className="stat-card-brand">
          <div className="stat-content">
            <div className="stat-icon in-progress">
              <ClockIcon />
            </div>
            <div className="stat-info">
              <h6>In Progress</h6>
              <h2>{statusCounts["in-progress"]}</h2>
            </div>
          </div>
        </div>
        
        <div className="stat-card-brand">
          <div className="stat-content">
            <div className="stat-icon resolved">
              <CheckIcon />
            </div>
            <div className="stat-info">
              <h6>Resolved</h6>
              <h2>{statusCounts.resolved}</h2>
            </div>
          </div>
        </div>
        
        <div className="stat-card-brand">
          <div className="stat-content">
            <div className="stat-icon credits">
              <CreditIcon />
            </div>
            <div className="stat-info">
              <h6>Credit Balance</h6>
              <h2>1,250</h2>
            </div>
          </div>
          <Link to="/brand/billing" className="stretched-link"></Link>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="main-content">
          <div className="card">
            <div className="card-header">
              <h4>Recent Tickets</h4>
            </div>
            <div className="card-body">
              <div className="table-responsive">
                <table className="table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th className="hide-mobile">Customer</th>
                      <th>Status</th>
                      <th className="hide-mobile">Date</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tickets.map(ticket => (
                      <tr key={ticket.id}>
                        <td>#{ticket.id}</td>
                        <td>{ticket.title}</td>
                        <td className="hide-mobile">{ticket.owner?.full_name || 'N/A'}</td>
                        <td><span className={`badge badge-status badge-${ticket.status.replace(/[^a-z]/g, '-')}`}>{ticket.status}</span></td>
                        <td className="hide-mobile">{new Date(ticket.created_at).toLocaleDateString()}</td>
                        <td>
                          <Link to={`/brand/tickets/${ticket.id}`} className="btn btn-sm btn-primary view-btn">
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div className="sidebar">
          <div className="card">
            <div className="card-header">
              <h4>Settings & Management</h4>
            </div>
            <div className="list-group list-group-flush">
              <Link to="/brand/analytics" className="list-group-item list-group-item-action">
                <span className="sidebar-link-icon me-2" role="img" aria-label="analytics">📊</span> Analytics Dashboard
              </Link>
              <Link to="/brand/team" className="list-group-item list-group-item-action">
                <span className="sidebar-link-icon me-2" role="img" aria-label="team">👥</span> Manage Team
              </Link>
              <Link to="/brand/settings" className="list-group-item list-group-item-action">
                <span className="sidebar-link-icon me-2" role="img" aria-label="settings">⚙️</span> Brand Settings
              </Link>
              <Link to="/brand/billing" className="list-group-item list-group-item-action">
                <span className="sidebar-link-icon me-2" role="img" aria-label="billing">💳</span> Manage Billing
              </Link>
              <Link to="/brand/manage-brands" className="list-group-item list-group-item-action">
                <span className="sidebar-link-icon me-2" role="img" aria-label="brands">🏢</span> Manage Brands
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BrandDashboard;