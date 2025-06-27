// src/services/ticketService.js

import apiClient from './apiClient';

const ticketService = {
  /**
   * Fetch a paginated list of tickets for the brand
   * @param {number} skip  how many to skip (default 0)
   * @param {number} limit how many to take (default 50)
   */
  list: (skip = 0, limit = 50) =>
    apiClient.get('/tickets/brand', {
      params: { skip, limit },
    }),

  /**
   * Fetch aggregate statistics for brand tickets
   */
  stats: () =>
    apiClient.get('/tickets/brand/stats'),

  /**
   * Update the status of a ticket
   * @param {number|string} id     ticket ID
   * @param {string}        status new status (e.g. "open", "in_progress", "resolved")
   */
  updateStatus: (id, status) =>
    apiClient.put(`/tickets/brand/tickets/${id}/status`, { status }),

  /**
   * Assign a ticket to a specific brand user
   * @param {number|string} id         ticket ID
   * @param {number|string} assigneeId ID of the brand user to assign to
   */
  assign: (id, assigneeId) =>
    apiClient.put(
      `/tickets/brand/tickets/${id}/assign`,
      null,
      { params: { assignee: assigneeId } }
    ),

  /**
   * Fetch detailed information for a single ticket
   * @param {number|string} id ticket ID
   */
  getById: id =>
    apiClient.get(`/tickets/brand/tickets/${id}`),

  /**
   * Post a brand response to a ticket
   * @param {number|string} ticketId ID of the ticket
   * @param {string}        message  response message content
   */
  addResponse: (ticketId, message) =>
    apiClient.post(
      `/tickets/brand/tickets/${ticketId}/response`,
      { message }
    ),
};

export default ticketService;
