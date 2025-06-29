import React from 'react';

const ResponsiveTest = () => {
  return (
    <div className="container">
      <h1 className="text-center mb-4">Responsive Design Test</h1>
      
      {/* Responsive Grid Test */}
      <div className="stats-grid mb-4">
        <div className="stat-card">
          <h2>1</h2>
          <p>Mobile First</p>
        </div>
        <div className="stat-card">
          <h2>2</h2>
          <p>Responsive Grid</p>
        </div>
        <div className="stat-card">
          <h2>3</h2>
          <p>Touch Friendly</p>
        </div>
        <div className="stat-card">
          <h2>4</h2>
          <p>Modern UI</p>
        </div>
      </div>

      {/* Responsive Button Group Test */}
      <div className="btn-group mb-4">
        <button className="btn btn-primary">Primary</button>
        <button className="btn btn-secondary">Secondary</button>
        <button className="btn btn-success">Success</button>
      </div>

      {/* Responsive Table Test */}
      <div className="card mb-4">
        <div className="card-header">
          <h4>Responsive Table</h4>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th className="hide-mobile">Email</th>
                  <th>Status</th>
                  <th className="hide-mobile">Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>#1</td>
                  <td>John Doe</td>
                  <td className="hide-mobile">john@example.com</td>
                  <td><span className="badge badge-primary">Active</span></td>
                  <td className="hide-mobile">2024-01-15</td>
                  <td><button className="btn btn-sm btn-outline-primary">View</button></td>
                </tr>
                <tr>
                  <td>#2</td>
                  <td>Jane Smith</td>
                  <td className="hide-mobile">jane@example.com</td>
                  <td><span className="badge badge-success">Completed</span></td>
                  <td className="hide-mobile">2024-01-14</td>
                  <td><button className="btn btn-sm btn-outline-primary">View</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Responsive Form Test */}
      <div className="card">
        <div className="card-header">
          <h4>Responsive Form</h4>
        </div>
        <div className="card-body">
          <form>
            <div className="form-group">
              <label className="form-label">Name</label>
              <input type="text" className="form-control" placeholder="Enter your name" />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input type="email" className="form-control" placeholder="Enter your email" />
            </div>
            <div className="form-group">
              <label className="form-label">Message</label>
              <textarea className="form-control" rows="3" placeholder="Enter your message"></textarea>
            </div>
            <div className="btn-group">
              <button type="submit" className="btn btn-primary">Submit</button>
              <button type="button" className="btn btn-secondary">Cancel</button>
            </div>
          </form>
        </div>
      </div>

      {/* Responsive Utilities Test */}
      <div className="mt-4">
        <h4>Responsive Utilities</h4>
        <div className="grid grid-1 gap-3">
          <div className="card">
            <div className="card-body">
              <p className="mobile-only">This text is only visible on mobile devices</p>
              <p className="desktop-only">This text is only visible on desktop devices</p>
              <p className="hide-mobile">This text is hidden on mobile devices</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponsiveTest; 