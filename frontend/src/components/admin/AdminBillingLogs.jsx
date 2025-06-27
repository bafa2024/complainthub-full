import React from 'react';
import { Link } from 'react-router-dom';

const AdminBillingLogs = () => {
    // Mock data for demonstration
    const mockLogs = [
        { id: 1, brand: 'E-Commerce Inc.', type: 'Charge', amount: -50, date: '2025-06-27', description: 'Unresolved Ticket #2' },
        { id: 2, brand: 'SaaS Platform', type: 'Top-up', amount: 500, date: '2025-06-26', description: 'Manual credit addition' },
        { id: 3, brand: 'E-Commerce Inc.', type: 'Charge', amount: -50, date: '2025-06-25', description: 'Unresolved Ticket #1' },
    ];

    return (
        <div className="container mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>Billing Logs</h1>
                <Link to="/admin/dashboard" className="btn btn-secondary">Back to Dashboard</Link>
            </div>
            <div className="card">
                <div className="card-body">
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>Log ID</th>
                                <th>Brand</th>
                                <th>Type</th>
                                <th>Amount (Credits)</th>
                                <th>Date</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {mockLogs.map(log => (
                                <tr key={log.id}>
                                    <td>{log.id}</td>
                                    <td>{log.brand}</td>
                                    <td>
                                        <span className={`badge ${log.type === 'Charge' ? 'bg-danger' : 'bg-success'}`}>
                                            {log.type}
                                        </span>
                                    </td>
                                    <td>{log.amount}</td>
                                    <td>{log.date}</td>
                                    <td>{log.description}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminBillingLogs;