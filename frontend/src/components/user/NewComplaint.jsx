// frontend/src/components/user/NewComplaint.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import brandService from '../../services/brandService';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './NewComplaint.css';

const NewComplaint = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [brandId, setBrandId] = useState('');
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBrands = async () => {
      try {
        setLoading(true);
        const brandsData = await brandService.getBrands();
        setBrands(brandsData);
        setError('');
      } catch (err) {
        setError('Failed to load brands. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchBrands();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !description || !brandId) {
      setError('All fields are required.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const ticketData = {
        title,
        description,
        brand_id: parseInt(brandId, 10),
        channel: 'web', // Set channel as 'web' for complaints lodged here
      };
      await ticketService.createTicket(ticketData);
      navigate('/dashboard'); // Redirect to dashboard on success
    } catch (err) {
      setError('Failed to submit complaint. Please try again.');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="new-complaint-container">
      <form onSubmit={handleSubmit} className="new-complaint-form">
        <h2>Lodge a New Complaint</h2>
        {error && <p className="error-message">{error}</p>}

        <div className="form-group">
          <label htmlFor="brand">Brand</label>
          <select
            id="brand"
            value={brandId}
            onChange={(e) => setBrandId(e.target.value)}
            required
          >
            <option value="" disabled>Select a brand</option>
            {brands.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="title">Complaint Title</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Late delivery for order #123"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Full Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="8"
            placeholder="Please provide all relevant details about your issue."
            required
          ></textarea>
        </div>

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Submitting...' : 'Submit Complaint'}
        </button>
      </form>
    </div>
  );
};

export default NewComplaint;