// src/utils/constants.js

export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const USER_ROLES = {
  USER: 'user',
  BRAND: 'brand',
  ADMIN: 'admin',
};

export const TICKET_STATUS = {
  NEW: 'new',
  PROGRESS: 'progress',
  RESOLVED: 'resolved',
};

export const TICKET_CATEGORIES = {
  COMPLAINT: 'complaint',
  FEEDBACK: 'feedback',
  SUGGESTION: 'suggestion',
  SUPPORT: 'support',
};

export const CHANNELS = {
  VOICE: 'voice',
  WHATSAPP: 'whatsapp',
  TELEGRAM: 'telegram',
  INSTAGRAM: 'instagram',
  LINKEDIN: 'linkedin',
  WEB: 'web',
  OTHER: 'other',
};

export const URGENCY_LEVELS = {
  LOW: 0,
  MEDIUM: 1,
  HIGH: 2,
  CRITICAL: 3,
};

export const RATING_SCALE = {
  MIN: 0,
  MAX: 5,
};

export const COMPLAINT_CHARGE = {
  AMOUNT: 50, // Rs. 50
  FREE_WINDOW_HOURS: 24,
};

export const RECORDING_CONFIG = {
  MAX_DURATION_MINUTES: 3,
  AUDIO_FORMAT: 'webm',
};

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
};

export const TOLL_FREE_NUMBERS = {
  MAIN: '1-800-COMPLAIN',
  PROVIDERS: ['twilio', 'knowlarity', 'exotel', 'ozonetel', 'myoperator'],
};

export const CRM_SYSTEMS = {
  SALESFORCE: 'salesforce',
  ZOHO: 'zoho',
  FRESHWORKS: 'freshworks',
  KAPTURE: 'kapture',
  LEADSQUARED: 'leadsquared',
};

export const LANGUAGES = {
  EN: { code: 'en', name: 'English' },
  HI: { code: 'hi', name: 'Hindi' },
  // Add more languages as needed
};

export const STATUS_COLORS = {
  new: '#fff3cd',
  progress: '#cce5ff',
  resolved: '#d4edda',
  urgent: '#f8d7da',
};

export const NOTIFICATION_TYPES = {
  NEW_COMPLAINT: 'new_complaint',
  STATUS_UPDATE: 'status_update',
  RESOLUTION_CONFIRMATION: 'resolution_confirmation',
  CREDIT_LOW: 'credit_low',
  PAYMENT_SUCCESS: 'payment_success',
};

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  SESSION_EXPIRED: 'Your session has expired. Please login again.',
  GENERIC_ERROR: 'Something went wrong. Please try again.',
};

export const SUCCESS_MESSAGES = {
  COMPLAINT_SUBMITTED: 'Your complaint has been submitted successfully.',
  RATING_SUBMITTED: 'Thank you for your feedback!',
  PROFILE_UPDATED: 'Profile updated successfully.',
  CREDITS_ADDED: 'Credits added successfully.',
};