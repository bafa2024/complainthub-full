import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import TicketCard from '../shared/TicketCard';
import './UserDashboard.css';

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
    <div className="user-dashboard">
      {/* Header Section */}
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">
            <i className="fas fa-tachometer-alt me-2"></i>
            My Dashboard
          </h1>
          <p className="page-subtitle">Track and manage your complaints</p>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid mb-4 grid grid-1 gap-4">
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-ticket-alt"></i>
              </div>
              <h2 className="stat-number text-2xl">{tickets.length}</h2>
              <p className="stat-label text-base">Total Tickets</p>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-clock"></i>
              </div>
              <h2 className="stat-number text-2xl">{statusCounts.new + statusCounts['in-progress']}</h2>
              <p className="stat-label text-base">Active Tickets</p>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-check-circle"></i>
              </div>
              <h2 className="stat-number text-2xl">{statusCounts.resolved}</h2>
              <p className="stat-label text-base">Resolved Tickets</p>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-chart-line"></i>
              </div>
              <h2 className="stat-number text-2xl">
                {tickets.length > 0 ? Math.round((statusCounts.resolved / tickets.length) * 100) : 0}%
              </h2>
              <p className="stat-label text-base">Resolution Rate</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="page-container">
        <div className="filters-section card mb-4">
          <div className="card-body">
            <div className="filters-header">
              <h3 className="filters-title">Filters & Search</h3>
              <div className="view-controls">
                <button 
                  className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                  onClick={() => setViewMode('list')}
                >
                  <i className="fas fa-list"></i> List
                </button>
                <button 
                  className={`view-btn ${viewMode === 'timeline' ? 'active' : ''}`}
                  onClick={() => setViewMode('timeline')}
                >
                  <i className="fas fa-stream"></i> Timeline
                </button>
              </div>
            </div>

            <div className="filters-grid">
              <div className="filter-group">
                <label>Search</label>
                <input
                  type="text"
                  placeholder="Search tickets..."
                  value={filters.searchQuery}
                  onChange={(e) => handleFilterChange('searchQuery', e.target.value)}
                  className="form-control"
                />
              </div>

              <div className="filter-group">
                <label>Status</label>
                <select 
                  value={filters.status} 
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="form-select"
                >
                  <option value="">All Status</option>
                  <option value="new">New</option>
                  <option value="in-progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div className="filter-group">
                <label>Brand</label>
                <select 
                  value={filters.brand} 
                  onChange={(e) => handleFilterChange('brand', e.target.value)}
                  className="form-select"
                >
                  <option value="">All Brands</option>
                  {brands.map(brand => (
                    <option key={brand} value={brand}>{brand}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>Date Range</label>
                <select 
                  value={filters.dateRange} 
                  onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                  className="form-select"
                >
                  <option value="all">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </select>
              </div>

              <div className="filter-group">
                <label>Sort By</label>
                <select 
                  value={sortBy} 
                  onChange={(e) => setSortBy(e.target.value)}
                  className="form-select"
                >
                  <option value="date">Date</option>
                  <option value="status">Status</option>
                  <option value="brand">Brand</option>
                  <option value="urgency">Urgency</option>
                </select>
              </div>

              <div className="filter-group">
                <button onClick={clearFilters} className="btn btn-outline-secondary">
                  <i className="fas fa-times"></i> Clear Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tickets Section */}
      <div className="page-container">
        <div className="tickets-header">
          <h2 className="tickets-title">
            <i className="fas fa-list me-2"></i>
            My Tickets ({filteredTickets.length})
          </h2>
          <Link to="/new-complaint" className="btn btn-primary">
            <i className="fas fa-plus me-2"></i>
            New Complaint
          </Link>
        </div>

        {filteredTickets.length > 0 ? (
          viewMode === 'list' ? (
            <div className="tickets-list grid grid-1 gap-4">
              {filteredTickets.map((ticket) => (
                <TicketCard key={ticket.id} ticket={ticket} linkPrefix="/tickets" />
              ))}
            </div>
          ) : (
            <div className="timeline-view">
              {getTimelineData().map((day) => (
                <div key={day.date} className="timeline-day">
                  <div className="timeline-date">{day.date}</div>
                  <div className="timeline-tickets">
                    {day.tickets.map((ticket) => (
                      <div key={ticket.id} className="timeline-ticket">
                        <div className="timeline-ticket-header">
                          <span className={`status-badge status-${ticket.status}`}>
                            {ticket.status.replace('-', ' ')}
                          </span>
                          <span className="ticket-time">
                            {new Date(ticket.created_at).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="timeline-ticket-content">
                          <h4 className="ticket-title">
                            <Link to={`/tickets/${ticket.id}`}>
                              {ticket.title}
                            </Link>
                          </h4>
                          <p className="ticket-brand">{ticket.brand?.name}</p>
                          <p className="ticket-description">
                            {ticket.description?.substring(0, 100)}...
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )
        ) : (
          <div className="card">
            <div className="card-body text-center">
              <div className="empty-state">
                <i className="fas fa-inbox fa-3x text-muted mb-3"></i>
                <h3 className="text-xl mb-3">No Tickets Found</h3>
                <p className="text-base text-muted mb-4">
                  {tickets.length === 0 
                    ? "You haven't submitted any complaints yet. Start by lodging your first complaint!"
                    : "No tickets match your current filters. Try adjusting your search criteria."
                  }
                </p>
                {tickets.length === 0 && (
                  <Link to="/new-complaint" className="btn btn-primary w-100">
                    <i className="fas fa-plus me-2"></i>
                    Lodge Your First Complaint
                  </Link>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;