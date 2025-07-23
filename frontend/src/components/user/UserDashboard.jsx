import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import TicketCard from '../shared/TicketCard';

const UserDashboard = () => {
  const [tickets, setTickets] = useState([]);
  const [filteredTickets, setFilteredTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'timeline'
  const [filters, setFilters] = useState({
    status: '',
    brand: '',
    dateRange: 'all',
    searchQuery: ''
  });
  const [sortBy, setSortBy] = useState('date');

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        setLoading(true);
        const userTickets = await ticketService.getTickets();
        setTickets(userTickets);
        setFilteredTickets(userTickets);
        setError('');
      } catch (err) {
        setError('Failed to load tickets. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchTickets();
  }, []);

  useEffect(() => {
    // Apply filters and sorting
    let filtered = tickets.filter(ticket => {
      // Status filter
      if (filters.status && ticket.status !== filters.status) {
        return false;
      }
      
      // Brand filter
      if (filters.brand && ticket.brand?.name && 
          !ticket.brand.name.toLowerCase().includes(filters.brand.toLowerCase())) {
        return false;
      }
      
      // Search query
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        const titleMatch = ticket.title?.toLowerCase().includes(query);
        const descriptionMatch = ticket.description?.toLowerCase().includes(query);
        const brandMatch = ticket.brand?.name?.toLowerCase().includes(query);
        
        if (!titleMatch && !descriptionMatch && !brandMatch) {
          return false;
        }
      }
      
      // Date range filter
      if (filters.dateRange !== 'all') {
        const ticketDate = new Date(ticket.created_at);
        const now = new Date();
        const daysDiff = Math.floor((now - ticketDate) / (1000 * 60 * 60 * 24));
        
        switch (filters.dateRange) {
          case 'today':
            if (daysDiff !== 0) return false;
            break;
          case 'week':
            if (daysDiff > 7) return false;
            break;
          case 'month':
            if (daysDiff > 30) return false;
            break;
          default:
            break;
        }
      }
      
      return true;
    });

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'status':
          const statusOrder = { 'new': 1, 'in-progress': 2, 'resolved': 3, 'closed': 4 };
          return statusOrder[a.status] - statusOrder[b.status];
        case 'brand':
          return (a.brand?.name || '').localeCompare(b.brand?.name || '');
        case 'urgency':
          const urgencyOrder = { 'high': 3, 'medium': 2, 'low': 1 };
          return urgencyOrder[b.urgency] - urgencyOrder[a.urgency];
        default:
          return 0;
      }
    });

    setFilteredTickets(filtered);
  }, [tickets, filters, sortBy]);

  const getStatusCounts = () => {
    const counts = { new: 0, 'in-progress': 0, resolved: 0, closed: 0 };
    tickets.forEach(ticket => {
      if (ticket.status in counts) {
        counts[ticket.status]++;
      }
    });
    return counts;
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      status: '',
      brand: '',
      dateRange: 'all',
      searchQuery: ''
    });
    setSortBy('date');
  };

  const getTimelineData = () => {
    const timelineData = [];
    const sortedTickets = [...filteredTickets].sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    );

    sortedTickets.forEach(ticket => {
      const date = new Date(ticket.created_at).toDateString();
      const existingDay = timelineData.find(day => day.date === date);
      
      if (existingDay) {
        existingDay.tickets.push(ticket);
      } else {
        timelineData.push({
          date,
          tickets: [ticket]
        });
      }
    });

    return timelineData;
  };

  const statusCounts = getStatusCounts();
  const brands = [...new Set(tickets.map(t => t.brand?.name).filter(Boolean))];

  if (loading) return <LoadingSpinner />;

  return (
    <div className="min-vh-100 bg-light">
      <div className="container-fluid py-4">
        {/* Header Section */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="text-center">
              <h1 className="display-4 fw-bold text-dark mb-2">
                <i className="bi bi-speedometer2 me-3"></i>
                My Dashboard
              </h1>
              <p className="lead text-muted">Track and manage your complaints</p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="row mb-4 g-3">
          <div className="col-12 col-sm-6 col-lg-3">
            <div className="card bg-gradient-primary text-white border-0 shadow-sm h-100">
              <div className="card-body text-center">
                <div className="mb-3">
                  <i className="bi bi-ticket-detailed display-6"></i>
                </div>
                <h2 className="display-6 fw-bold mb-2">{tickets.length}</h2>
                <p className="mb-0 text-white-50">Total Tickets</p>
              </div>
            </div>
          </div>
          <div className="col-12 col-sm-6 col-lg-3">
            <div className="card bg-gradient-warning text-white border-0 shadow-sm h-100">
              <div className="card-body text-center">
                <div className="mb-3">
                  <i className="bi bi-clock display-6"></i>
                </div>
                <h2 className="display-6 fw-bold mb-2">{statusCounts.new + statusCounts['in-progress']}</h2>
                <p className="mb-0 text-white-50">Active Tickets</p>
              </div>
            </div>
          </div>
          <div className="col-12 col-sm-6 col-lg-3">
            <div className="card bg-gradient-success text-white border-0 shadow-sm h-100">
              <div className="card-body text-center">
                <div className="mb-3">
                  <i className="bi bi-check-circle display-6"></i>
                </div>
                <h2 className="display-6 fw-bold mb-2">{statusCounts.resolved}</h2>
                <p className="mb-0 text-white-50">Resolved Tickets</p>
              </div>
            </div>
          </div>
          <div className="col-12 col-sm-6 col-lg-3">
            <div className="card bg-gradient-info text-white border-0 shadow-sm h-100">
              <div className="card-body text-center">
                <div className="mb-3">
                  <i className="bi bi-graph-up display-6"></i>
                </div>
                <h2 className="display-6 fw-bold mb-2">
                  {tickets.length > 0 ? Math.round((statusCounts.resolved / tickets.length) * 100) : 0}%
                </h2>
                <p className="mb-0 text-white-50">Resolution Rate</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Controls */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="card border-0 shadow-sm">
              <div className="card-body">
                <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4">
                  <h3 className="h5 fw-bold text-dark mb-0">Filters & Search</h3>
                  <div className="btn-group mt-3 mt-md-0" role="group">
                    <button 
                      className={`btn btn-sm ${viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'}`}
                      onClick={() => setViewMode('list')}
                    >
                      <i className="bi bi-list me-1"></i> List
                    </button>
                    <button 
                      className={`btn btn-sm ${viewMode === 'timeline' ? 'btn-primary' : 'btn-outline-primary'}`}
                      onClick={() => setViewMode('timeline')}
                    >
                      <i className="bi bi-calendar3 me-1"></i> Timeline
                    </button>
                  </div>
                </div>

                <div className="row g-3">
                  <div className="col-12 col-md-6 col-lg-3">
                    <label className="form-label fw-semibold small">Search</label>
                    <input
                      type="text"
                      placeholder="Search tickets..."
                      value={filters.searchQuery}
                      onChange={(e) => handleFilterChange('searchQuery', e.target.value)}
                      className="form-control form-control-sm"
                    />
                  </div>

                  <div className="col-12 col-md-6 col-lg-2">
                    <label className="form-label fw-semibold small">Status</label>
                    <select 
                      value={filters.status} 
                      onChange={(e) => handleFilterChange('status', e.target.value)}
                      className="form-select form-select-sm"
                    >
                      <option value="">All Status</option>
                      <option value="new">New</option>
                      <option value="in-progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                      <option value="closed">Closed</option>
                    </select>
                  </div>

                  <div className="col-12 col-md-6 col-lg-2">
                    <label className="form-label fw-semibold small">Brand</label>
                    <select 
                      value={filters.brand} 
                      onChange={(e) => handleFilterChange('brand', e.target.value)}
                      className="form-select form-select-sm"
                    >
                      <option value="">All Brands</option>
                      {brands.map(brand => (
                        <option key={brand} value={brand}>{brand}</option>
                      ))}
                    </select>
                  </div>

                  <div className="col-12 col-md-6 col-lg-2">
                    <label className="form-label fw-semibold small">Date Range</label>
                    <select 
                      value={filters.dateRange} 
                      onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                      className="form-select form-select-sm"
                    >
                      <option value="all">All Time</option>
                      <option value="today">Today</option>
                      <option value="week">This Week</option>
                      <option value="month">This Month</option>
                    </select>
                  </div>

                  <div className="col-12 col-md-6 col-lg-2">
                    <label className="form-label fw-semibold small">Sort By</label>
                    <select 
                      value={sortBy} 
                      onChange={(e) => setSortBy(e.target.value)}
                      className="form-select form-select-sm"
                    >
                      <option value="date">Date</option>
                      <option value="status">Status</option>
                      <option value="brand">Brand</option>
                      <option value="urgency">Urgency</option>
                    </select>
                  </div>

                  <div className="col-12 col-md-6 col-lg-1">
                    <label className="form-label fw-semibold small">&nbsp;</label>
                    <button onClick={clearFilters} className="btn btn-outline-secondary btn-sm w-100">
                      <i className="bi bi-x-circle me-1"></i> Clear
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tickets Section */}
        <div className="row">
          <div className="col-12">
            <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4">
              <h2 className="h4 fw-bold text-dark mb-0">
                <i className="bi bi-list me-2"></i>
                My Tickets ({filteredTickets.length})
              </h2>
              <div className="d-flex flex-column align-items-end">
                <div className="btn-group mt-3 mt-md-0" role="group">
                  <Link to="/submit-complaint" className="btn btn-primary">
                    <i className="bi bi-globe me-2"></i>
                    Public Form
                  </Link>
                  <Link to="/new-complaint" className="btn btn-outline-primary">
                    <i className="bi bi-shield-lock me-2"></i>
                    Private Form
                  </Link>
                </div>
                <small className="text-muted mt-1">
                  <i className="bi bi-info-circle me-1"></i>
                  Public: Quick form, Private: Multi-step with voice recording
                </small>
              </div>
            </div>

            {filteredTickets.length > 0 ? (
              viewMode === 'list' ? (
                <div className="row g-3">
                  {filteredTickets.map((ticket) => (
                    <div key={ticket.id} className="col-12">
                      <TicketCard ticket={ticket} linkPrefix="/tickets" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card border-0 shadow-sm">
                  <div className="card-body p-0">
                    {getTimelineData().map((day) => (
                      <div key={day.date} className="border-bottom">
                        <div className="bg-light px-4 py-3">
                          <h6 className="fw-bold text-dark mb-0">{day.date}</h6>
                        </div>
                        <div className="p-4">
                          {day.tickets.map((ticket) => (
                            <div key={ticket.id} className="card mb-3 border-0 bg-light">
                              <div className="card-body">
                                <div className="d-flex justify-content-between align-items-start mb-2">
                                  <span className={`badge ${ticket.status === 'new' ? 'bg-primary' : 
                                    ticket.status === 'in-progress' ? 'bg-warning' : 
                                    ticket.status === 'resolved' ? 'bg-success' : 'bg-secondary'}`}>
                                    {ticket.status.replace('-', ' ')}
                                  </span>
                                  <small className="text-muted">
                                    {new Date(ticket.created_at).toLocaleTimeString()}
                                  </small>
                                </div>
                                <h6 className="card-title mb-2">
                                  <Link to={`/tickets/${ticket.id}`} className="text-decoration-none">
                                    {ticket.title}
                                  </Link>
                                </h6>
                                <p className="text-muted small mb-2">{ticket.brand?.name}</p>
                                <p className="card-text small">
                                  {ticket.description?.substring(0, 100)}...
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            ) : (
              <div className="card border-0 shadow-sm">
                <div className="card-body text-center py-5">
                  <div className="mb-4">
                    <i className="bi bi-inbox display-1 text-muted"></i>
                  </div>
                  <h3 className="h5 mb-3">No Tickets Found</h3>
                  <p className="text-muted mb-4">
                    {tickets.length === 0 
                      ? "You haven't submitted any complaints yet. Start by lodging your first complaint!"
                      : "No tickets match your current filters. Try adjusting your search criteria."
                    }
                  </p>
                  {tickets.length === 0 && (
                    <div className="d-flex flex-column flex-sm-row gap-2 justify-content-center">
                      <Link to="/submit-complaint" className="btn btn-primary">
                        <i className="bi bi-globe me-2"></i>
                        Public Form
                      </Link>
                      <Link to="/new-complaint" className="btn btn-outline-primary">
                        <i className="bi bi-shield-lock me-2"></i>
                        Private Form
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;