import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import brandService from '../../services/brandService';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import VoiceRecorder from '../shared/VoiceRecorder'; // Import the new component

const NewComplaint = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [brandId, setBrandId] = useState('');
  const [brands, setBrands] = useState([]);
  const [audioBlob, setAudioBlob] = useState(null); // State to hold the recording
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // This uses the mocked service for now
    const fetchBrands = async () => {
        try {
            setLoading(true);
            const brandsData = await brandService.getBrands();
            setBrands(brandsData || []); // Ensure brands is always an array
        } catch (err) {
            console.error(err);
            setError('Could not load brand information.');
        } finally {
            setLoading(false);
        }
    };
    fetchBrands();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !brandId || (!description && !audioBlob)) {
      setError('Please provide a title, select a brand, and either type a description or record a voice note.');
      return;
    }

    setSubmitting(true);
    setError('');

    // --- MOCKED SUBMISSION FOR UI TESTING ---
    console.log("Submitting Complaint:", { title, brandId, description });
    if (audioBlob) {
        console.log("Attaching voice note:", audioBlob);
    }
    alert("Complaint submitted successfully (Mocked)!");
    setSubmitting(false);
    navigate('/dashboard');
    // The real backend logic would be here in a real scenario
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <form onSubmit={handleSubmit} className="card p-4">
            <h2 className="text-center mb-4">Lodge a New Complaint</h2>
            {error && <p className="alert alert-danger">{error}</p>}

            <div className="mb-3">
              <label htmlFor="brand" className="form-label">Brand</label>
              <select id="brand" className="form-select" value={brandId} onChange={(e) => setBrandId(e.target.value)} required>
                <option value="" disabled>Select a brand...</option>
                {brands.map((brand) => <option key={brand.id} value={brand.id}>{brand.name}</option>)}
              </select>
            </div>

            <div className="mb-3">
              <label htmlFor="title" className="form-label">Complaint Title</label>
              <input type="text" id="title" className="form-control" value={title} onChange={(e) => setTitle(e.target.value)} required />
            </div>

            <div className="mb-3">
              <label htmlFor="description" className="form-label">
                Option 1: Type Description
              </label>
              <textarea id="description" className="form-control" value={description} onChange={(e) => setDescription(e.target.value)} rows="5"></textarea>
            </div>
            
            <div className="text-center my-2 fw-bold">OR</div>

            <div className="mb-3">
              <label className="form-label">
                Option 2: Record Voice Complaint
              </label>
              <VoiceRecorder onRecordingComplete={(blob) => setAudioBlob(blob)} />
            </div>

            <button type="submit" className="btn btn-primary w-100" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Complaint'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default NewComplaint;
