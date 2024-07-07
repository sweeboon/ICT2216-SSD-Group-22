import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useAuth } from '../hooks/useAuth';
import '../css/AuditLogPage.css';

const AuditLogPage = () => {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchColumn, setSearchColumn] = useState('all');
  const { isLoggedIn, roles } = useAuth();
  const isAdmin = roles.includes('Admin');
  const [sortConfig, setSortConfig] = useState({ column: null, direction: 'asc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [logsPerPage] = useState(10);

  useEffect(() => {
    const fetchAuditLogs = async () => {
      if (isLoggedIn && isAdmin) {
        try {
          console.log('Fetching audit logs...');
          const response = await axios.get('/admin/audit_logs');
          console.log('Audit logs response:', response);
          setLogs(response.data);
          setError(''); // Clear any previous errors
        } catch (error) {
          console.error('Error fetching audit logs:', error.response || error.message || error);
          setError('Error fetching audit logs');
        }
      } else {
        setError('User is not logged in or is not an admin, cannot fetch audit logs.');
        console.error('User is not logged in or is not an admin');
      }
    };

    fetchAuditLogs();
  }, [isLoggedIn, isAdmin]);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const filteredLogs = React.useMemo(() => {
    const queryParts = searchQuery.toLowerCase().split(' ');
    return logs.filter(log => {
      const logValues = searchColumn === 'all' 
        ? Object.keys(log).reduce((acc, key) => {
            if (key === 'timestamp') {
              acc.push(formatTimestamp(log[key]).toLowerCase());
            } else {
              acc.push(log[key].toString().toLowerCase());
            }
            return acc;
          }, [])
        : [log[searchColumn].toString().toLowerCase()];

      return queryParts.every(part => 
        logValues.some(value => value.includes(part))
      );
    });
  }, [logs, searchQuery, searchColumn]);

  const sortedLogs = React.useMemo(() => {
    if (sortConfig.column) {
      return [...filteredLogs].sort((a, b) => {
        const aValue = a[sortConfig.column];
        const bValue = b[sortConfig.column];

        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
        } else if (typeof aValue === 'string' && typeof bValue === 'string') {
          return sortConfig.direction === 'asc'
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
        } else if (aValue instanceof Date && bValue instanceof Date) {
          return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
        } else {
          return sortConfig.direction === 'asc'
            ? String(aValue).localeCompare(String(bValue))
            : String(bValue).localeCompare(String(aValue));
        }
      });
    }
    return filteredLogs;
  }, [filteredLogs, sortConfig]);

  const handleSort = (column) => {
    let direction = 'asc';
    if (sortConfig.column === column && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ column, direction });
  };

  const indexOfLastLog = currentPage * logsPerPage;
  const indexOfFirstLog = indexOfLastLog - logsPerPage;
  const currentLogs = sortedLogs.slice(indexOfFirstLog, indexOfLastLog);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="audit-log-container">
      <h1>Audit Logs</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div className="audit-log-filters">
        <input
          type="text"
          placeholder="Search logs..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="audit-log-search-input"
        />
        <select
          value={searchColumn}
          onChange={(e) => setSearchColumn(e.target.value)}
          className="audit-log-column-select"
        >
          <option value="all">All Columns</option>
          <option value="id">ID</option>
          <option value="user_id">User ID</option>
          <option value="user_name">User Name</option>
          <option value="action">Action</option>
          <option value="details">Details</option>
          <option value="timestamp">Timestamp</option>
          <option value="ip_address">IP Address</option>
        </select>
      </div>
      <table className="audit-log-table">
        <thead>
          <tr>
            {['id', 'user_id', 'user_name', 'action', 'details', 'timestamp', 'ip_address'].map((column) => (
              <th
                key={column}
                className={sortConfig.column === column ? `sorted-${sortConfig.direction}` : ''}
                onClick={() => handleSort(column)}
              >
                {column.replace('_', ' ')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {currentLogs.map(log => (
            <tr key={log.id}>
              <td>{log.id}</td>
              <td>{log.user_id}</td>
              <td>{log.user_name}</td>
              <td>{log.action}</td>
              <td>{log.details}</td>
              <td>{formatTimestamp(log.timestamp)}</td>
              <td>{log.ip_address}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="audit-log-pagination">
        {Array.from({ length: Math.ceil(filteredLogs.length / logsPerPage) }, (_, i) => (
          <button
            key={i + 1}
            onClick={() => paginate(i + 1)}
            className={currentPage === i + 1 ? 'active' : ''}
          >
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
};

export default AuditLogPage;
