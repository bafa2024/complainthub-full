import React, { useState } from 'react';
import './SatisfactionRating.css'; // We will create this stylesheet

const StarIcon = ({ filled }) => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill={filled ? "#ffc107" : "#e4e5e9"} stroke={filled ? "#ffc107" : "#e4e5e9"} strokeWidth="1">
        <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
    </svg>
);

const SatisfactionRating = ({ onSubmit }) => {
    const [rating, setRating] = useState(0);
    const [hoverRating, setHoverRating] = useState(0);
    const [comment, setComment] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (rating === 0) {
            alert("Please select a star rating.");
            return;
        }
        onSubmit(rating, comment);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="star-rating mb-3">
                {[1, 2, 3, 4, 5].map((star) => (
                    <span
                        key={star}
                        className="star"
                        onMouseEnter={() => setHoverRating(star)}
                        onMouseLeave={() => setHoverRating(0)}
                        onClick={() => setRating(star)}
                    >
                        <StarIcon filled={hoverRating >= star || rating >= star} />
                    </span>
                ))}
            </div>
            <div className="mb-3">
                <textarea
                    className="form-control"
                    rows="3"
                    placeholder="Add an optional comment..."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                ></textarea>
            </div>
            <button type="submit" className="btn btn-primary">Submit Rating</button>
        </form>
    );
};

export default SatisfactionRating;