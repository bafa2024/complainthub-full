import React, { useState, useEffect } from 'react';
import './RatingComponent.css';

const RatingComponent = ({
  value = 0,
  maxValue = 5,
  size = 'medium', // 'small', 'medium', 'large'
  readonly = false,
  showValue = true,
  showLabel = true,
  onChange,
  onHover,
  className = '',
  disabled = false,
  color = 'gold', // 'gold', 'blue', 'green', 'red', 'purple'
  halfStars = false,
  labels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'],
  icon = 'star' // 'star', 'heart', 'thumbs-up', 'circle'
}) => {
  const [rating, setRating] = useState(value);
  const [hoverRating, setHoverRating] = useState(0);
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    setRating(value);
  }, [value]);

  const getIconClass = () => {
    switch (icon) {
      case 'heart':
        return 'fas fa-heart';
      case 'thumbs-up':
        return 'fas fa-thumbs-up';
      case 'circle':
        return 'fas fa-circle';
      default:
        return 'fas fa-star';
    }
  };

  const getColorClass = () => {
    switch (color) {
      case 'blue':
        return 'rating-blue';
      case 'green':
        return 'rating-green';
      case 'red':
        return 'rating-red';
      case 'purple':
        return 'rating-purple';
      default:
        return 'rating-gold';
    }
  };

  const handleMouseEnter = (index) => {
    if (readonly || disabled) return;
    setHoverRating(index);
    setIsHovering(true);
    onHover?.(index);
  };

  const handleMouseLeave = () => {
    if (readonly || disabled) return;
    setHoverRating(0);
    setIsHovering(false);
    onHover?.(0);
  };

  const handleClick = (index) => {
    if (readonly || disabled) return;
    const newRating = index === rating ? 0 : index;
    setRating(newRating);
    onChange?.(newRating);
  };

  const renderStar = (index) => {
    const currentRating = isHovering ? hoverRating : rating;
    const isFilled = index <= currentRating;
    const isHalf = halfStars && index === Math.ceil(currentRating) && currentRating % 1 !== 0;

    return (
      <span
        key={index}
        className={`rating-icon ${getColorClass()} ${getIconClass()} ${
          isFilled ? 'filled' : ''
        } ${isHalf ? 'half' : ''} ${size}`}
        onMouseEnter={() => handleMouseEnter(index)}
        onMouseLeave={handleMouseLeave}
        onClick={() => handleClick(index)}
        style={{ cursor: readonly || disabled ? 'default' : 'pointer' }}
        role={readonly ? 'img' : 'button'}
        aria-label={`Rate ${index} ${icon}${index !== 1 ? 's' : ''}`}
        tabIndex={readonly || disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleClick(index);
          }
        }}
      >
        {isHalf && (
          <span className="half-star-overlay">
            <i className={getIconClass()}></i>
          </span>
        )}
      </span>
    );
  };

  const getRatingLabel = () => {
    if (!showLabel || !labels || labels.length === 0) return null;
    
    const currentRating = isHovering ? hoverRating : rating;
    const labelIndex = Math.floor(currentRating) - 1;
    
    if (labelIndex >= 0 && labelIndex < labels.length) {
      return labels[labelIndex];
    }
    
    return '';
  };

  const getRatingText = () => {
    const currentRating = isHovering ? hoverRating : rating;
    if (currentRating === 0) return 'No rating';
    if (currentRating === 1) return '1 star';
    return `${currentRating} stars`;
  };

  return (
    <div className={`rating-component ${className} ${disabled ? 'disabled' : ''}`}>
      <div className="rating-stars">
        {Array.from({ length: maxValue }, (_, index) => renderStar(index + 1))}
      </div>
      
      {showValue && (
        <div className="rating-value">
          <span className="rating-number">{rating.toFixed(halfStars ? 1 : 0)}</span>
          <span className="rating-max">/{maxValue}</span>
        </div>
      )}
      
      {showLabel && getRatingLabel() && (
        <div className="rating-label">
          {getRatingLabel()}
        </div>
      )}
      
      <span className="sr-only">{getRatingText()}</span>
    </div>
  );
};

// Rating Display Component (Read-only)
export const RatingDisplay = ({ 
  value, 
  maxValue = 5, 
  size = 'medium',
  showValue = true,
  showLabel = true,
  color = 'gold',
  icon = 'star',
  labels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'],
  className = ''
}) => {
  return (
    <RatingComponent
      value={value}
      maxValue={maxValue}
      size={size}
      readonly={true}
      showValue={showValue}
      showLabel={showLabel}
      color={color}
      icon={icon}
      labels={labels}
      className={className}
    />
  );
};

// Rating Input Component (Interactive)
export const RatingInput = ({ 
  value, 
  maxValue = 5, 
  size = 'medium',
  showValue = true,
  showLabel = true,
  color = 'gold',
  icon = 'star',
  labels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'],
  halfStars = false,
  onChange,
  onHover,
  disabled = false,
  className = ''
}) => {
  return (
    <RatingComponent
      value={value}
      maxValue={maxValue}
      size={size}
      readonly={false}
      showValue={showValue}
      showLabel={showLabel}
      color={color}
      icon={icon}
      labels={labels}
      halfStars={halfStars}
      onChange={onChange}
      onHover={onHover}
      disabled={disabled}
      className={className}
    />
  );
};

export default RatingComponent; 