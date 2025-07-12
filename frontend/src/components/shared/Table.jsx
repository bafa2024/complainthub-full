import React, { useState, useMemo } from 'react';
import './Table.css';

const Table = ({
  data = [],
  columns = [],
  pageSize = 10,
  searchable = true,
  sortable = true,
  filterable = true,
  selectable = false,
  onRowClick,
  onSelectionChange,
  className = '',
  emptyMessage = 'No data available',
  loading = false
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const [selectedRows, setSelectedRows] = useState(new Set());

  // Memoized filtered and sorted data
  const processedData = useMemo(() => {
    let result = [...data];

    // Apply search
    if (searchable && searchTerm) {
      result = result.filter(row => {
        return columns.some(column => {
          const value = column.accessor ? column.accessor(row) : row[column.key];
          if (value == null) return false;
          return String(value).toLowerCase().includes(searchTerm.toLowerCase());
        });
      });
    }

    // Apply filters
    if (filterable) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== '') {
          result = result.filter(row => {
            const cellValue = row[key];
            if (typeof value === 'function') {
              return value(cellValue);
            }
            return String(cellValue).toLowerCase().includes(String(value).toLowerCase());
          });
        }
      });
    }

    // Apply sorting
    if (sortable && sortConfig.key) {
      result.sort((a, b) => {
        const aValue = sortConfig.accessor ? sortConfig.accessor(a) : a[sortConfig.key];
        const bValue = sortConfig.accessor ? sortConfig.accessor(b) : b[sortConfig.key];

        if (aValue == null && bValue == null) return 0;
        if (aValue == null) return 1;
        if (bValue == null) return -1;

        let comparison = 0;
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          comparison = aValue.localeCompare(bValue);
        } else {
          comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        }

        return sortConfig.direction === 'desc' ? -comparison : comparison;
      });
    }

    return result;
  }, [data, searchTerm, filters, sortConfig, columns, searchable, filterable, sortable]);

  // Pagination
  const totalPages = Math.ceil(processedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = processedData.slice(startIndex, endIndex);

  // Handle sorting
  const handleSort = (key, accessor) => {
    setSortConfig(prevConfig => ({
      key,
      accessor,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Handle row selection
  const handleRowSelect = (rowId) => {
    const newSelection = new Set(selectedRows);
    if (newSelection.has(rowId)) {
      newSelection.delete(rowId);
    } else {
      newSelection.add(rowId);
    }
    setSelectedRows(newSelection);
    onSelectionChange?.(Array.from(newSelection));
  };

  // Handle select all
  const handleSelectAll = () => {
    if (selectedRows.size === paginatedData.length) {
      setSelectedRows(new Set());
      onSelectionChange?.([]);
    } else {
      const allIds = paginatedData.map(row => row.id);
      setSelectedRows(new Set(allIds));
      onSelectionChange?.(allIds);
    }
  };

  // Get sort icon
  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return <i className="fas fa-sort text-muted"></i>;
    }
    return sortConfig.direction === 'asc' 
      ? <i className="fas fa-sort-up text-primary"></i>
      : <i className="fas fa-sort-down text-primary"></i>;
  };

  // Render cell content
  const renderCell = (row, column) => {
    const value = column.accessor ? column.accessor(row) : row[column.key];
    
    if (column.render) {
      return column.render(value, row);
    }

    if (column.type === 'date') {
      return new Date(value).toLocaleDateString();
    }

    if (column.type === 'datetime') {
      return new Date(value).toLocaleString();
    }

    if (column.type === 'currency') {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
      }).format(value);
    }

    if (column.type === 'number') {
      return new Intl.NumberFormat().format(value);
    }

    if (column.type === 'percentage') {
      return `${value}%`;
    }

    if (column.type === 'boolean') {
      return value ? (
        <i className="fas fa-check text-success"></i>
      ) : (
        <i className="fas fa-times text-danger"></i>
      );
    }

    return value || '-';
  };

  if (loading) {
    return (
      <div className={`table-container ${className}`}>
        <div className="table-loading">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p>Loading data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`table-container ${className}`}>
      {/* Table Controls */}
      <div className="table-controls">
        {/* Search */}
        {searchable && (
          <div className="table-search">
            <div className="search-input-group">
              <i className="fas fa-search search-icon"></i>
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="search-clear"
                >
                  <i className="fas fa-times"></i>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Filters */}
        {filterable && columns.some(col => col.filterable) && (
          <div className="table-filters">
            {columns
              .filter(col => col.filterable)
              .map(column => (
                <div key={column.key} className="filter-group">
                  <label className="filter-label">{column.label}</label>
                  {column.filterType === 'select' ? (
                    <select
                      value={filters[column.key] || ''}
                      onChange={(e) => setFilters(prev => ({
                        ...prev,
                        [column.key]: e.target.value
                      }))}
                      className="filter-select"
                    >
                      <option value="">All</option>
                      {column.filterOptions?.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      placeholder={`Filter ${column.label}...`}
                      value={filters[column.key] || ''}
                      onChange={(e) => setFilters(prev => ({
                        ...prev,
                        [column.key]: e.target.value
                      }))}
                      className="filter-input"
                    />
                  )}
                </div>
              ))}
          </div>
        )}

        {/* Results Info */}
        <div className="table-info">
          <span>
            Showing {startIndex + 1} to {Math.min(endIndex, processedData.length)} of {processedData.length} results
          </span>
        </div>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              {selectable && (
                <th className="select-column">
                  <input
                    type="checkbox"
                    checked={selectedRows.size === paginatedData.length && paginatedData.length > 0}
                    onChange={handleSelectAll}
                    className="select-checkbox"
                  />
                </th>
              )}
              {columns.map(column => (
                <th
                  key={column.key}
                  className={`table-header ${sortable && column.sortable !== false ? 'sortable' : ''}`}
                  onClick={() => sortable && column.sortable !== false && handleSort(column.key, column.accessor)}
                >
                  <div className="header-content">
                    <span>{column.label}</span>
                    {sortable && column.sortable !== false && getSortIcon(column.key)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length + (selectable ? 1 : 0)} className="empty-state">
                  <div className="empty-content">
                    <i className="fas fa-inbox empty-icon"></i>
                    <p>{emptyMessage}</p>
                  </div>
                </td>
              </tr>
            ) : (
              paginatedData.map((row, index) => (
                <tr
                  key={row.id || index}
                  className={`table-row ${onRowClick ? 'clickable' : ''} ${selectedRows.has(row.id) ? 'selected' : ''}`}
                  onClick={() => onRowClick?.(row)}
                >
                  {selectable && (
                    <td className="select-column">
                      <input
                        type="checkbox"
                        checked={selectedRows.has(row.id)}
                        onChange={() => handleRowSelect(row.id)}
                        onClick={(e) => e.stopPropagation()}
                        className="select-checkbox"
                      />
                    </td>
                  )}
                  {columns.map(column => (
                    <td key={column.key} className={`table-cell ${column.className || ''}`}>
                      {renderCell(row, column)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="table-pagination">
          <div className="pagination-info">
            <span>
              Page {currentPage} of {totalPages}
            </span>
          </div>
          <div className="pagination-controls">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="pagination-btn"
            >
              <i className="fas fa-angle-double-left"></i>
            </button>
            <button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="pagination-btn"
            >
              <i className="fas fa-angle-left"></i>
            </button>
            
            {/* Page Numbers */}
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`pagination-btn ${currentPage === pageNum ? 'active' : ''}`}
                >
                  {pageNum}
                </button>
              );
            })}
            
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="pagination-btn"
            >
              <i className="fas fa-angle-right"></i>
            </button>
            <button
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
              className="pagination-btn"
            >
              <i className="fas fa-angle-double-right"></i>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Table;
