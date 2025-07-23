const cron = require('node-cron');
const ComplaintBot = require('./ai-bot');

class FollowupService {
    constructor(db) {
        this.db = db;
        this.aiBot = new ComplaintBot();
        
        // Follow-up configuration
        this.followupConfig = {
            initialDelay: 24, // hours
            reminderInterval: 48, // hours
            maxReminders: 3,
            escalationDelay: 72, // hours
            satisfactionSurveyDelay: 168 // hours (7 days)
        };

        // Setup automated follow-up tasks
        this.setupAutomatedFollowups();
    }

    // Setup automated follow-up tasks
    setupAutomatedFollowups() {
        // Check for initial follow-ups (every 6 hours)
        cron.schedule('0 */6 * * *', async () => {
            await this.checkInitialFollowups();
        });

        // Check for reminder follow-ups (every 12 hours)
        cron.schedule('0 */12 * * *', async () => {
            await this.checkReminderFollowups();
        });

        // Check for escalation (every 24 hours)
        cron.schedule('0 0 * * *', async () => {
            await this.checkEscalations();
        });

        // Send satisfaction surveys (daily at 9 AM)
        cron.schedule('0 9 * * *', async () => {
            await this.sendSatisfactionSurveys();
        });
    }

    // Check for initial follow-ups
    async checkInitialFollowups() {
        try {
            const tickets = await this.db.all(`
                SELECT t.*, b.name as brand_name, b.support_email, u.email as user_email, u.full_name
                FROM tickets t
                JOIN brands b ON t.brand_id = b.id
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.status = 'open'
                AND t.followup_sent = 0
                AND t.created_at < datetime('now', '-${this.followupConfig.initialDelay} hours')
            `);

            for (const ticket of tickets) {
                await this.sendInitialFollowup(ticket);
            }

            console.log(`Processed ${tickets.length} initial follow-ups`);
        } catch (error) {
            console.error('Initial follow-up check error:', error);
        }
    }

    // Send initial follow-up
    async sendInitialFollowup(ticket) {
        try {
            // Generate AI-powered follow-up message
            const message = await this.generateFollowupMessage(ticket, 'initial');
            
            // Send to brand
            await this.sendBrandNotification(ticket, message);
            
            // Send to user
            await this.sendUserNotification(ticket, message);
            
            // Update ticket
            await this.db.run(`
                UPDATE tickets 
                SET followup_sent = 1, 
                    last_followup = datetime('now'),
                    followup_count = 1
                WHERE id = ?
            `, [ticket.id]);

            // Log follow-up
            await this.logFollowup(ticket.id, 'initial', message);

            console.log(`Sent initial follow-up for ticket ${ticket.id}`);
        } catch (error) {
            console.error(`Error sending initial follow-up for ticket ${ticket.id}:`, error);
        }
    }

    // Check for reminder follow-ups
    async checkReminderFollowups() {
        try {
            const tickets = await this.db.all(`
                SELECT t.*, b.name as brand_name, b.support_email, u.email as user_email, u.full_name
                FROM tickets t
                JOIN brands b ON t.brand_id = b.id
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.status = 'open'
                AND t.followup_count < ?
                AND t.last_followup < datetime('now', '-${this.followupConfig.reminderInterval} hours')
            `, [this.followupConfig.maxReminders]);

            for (const ticket of tickets) {
                await this.sendReminderFollowup(ticket);
            }

            console.log(`Processed ${tickets.length} reminder follow-ups`);
        } catch (error) {
            console.error('Reminder follow-up check error:', error);
        }
    }

    // Send reminder follow-up
    async sendReminderFollowup(ticket) {
        try {
            const message = await this.generateFollowupMessage(ticket, 'reminder');
            
            // Send to brand
            await this.sendBrandNotification(ticket, message);
            
            // Send to user
            await this.sendUserNotification(ticket, message);
            
            // Update ticket
            await this.db.run(`
                UPDATE tickets 
                SET last_followup = datetime('now'),
                    followup_count = followup_count + 1
                WHERE id = ?
            `, [ticket.id]);

            // Log follow-up
            await this.logFollowup(ticket.id, 'reminder', message);

            console.log(`Sent reminder follow-up for ticket ${ticket.id}`);
        } catch (error) {
            console.error(`Error sending reminder follow-up for ticket ${ticket.id}:`, error);
        }
    }

    // Check for escalations
    async checkEscalations() {
        try {
            const tickets = await this.db.all(`
                SELECT t.*, b.name as brand_name, b.support_email, u.email as user_email, u.full_name
                FROM tickets t
                JOIN brands b ON t.brand_id = b.id
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.status = 'open'
                AND t.escalated = 0
                AND t.created_at < datetime('now', '-${this.followupConfig.escalationDelay} hours')
            `);

            for (const ticket of tickets) {
                await this.escalateTicket(ticket);
            }

            console.log(`Processed ${tickets.length} escalations`);
        } catch (error) {
            console.error('Escalation check error:', error);
        }
    }

    // Escalate ticket
    async escalateTicket(ticket) {
        try {
            // Generate escalation message
            const message = await this.generateFollowupMessage(ticket, 'escalation');
            
            // Send escalation to brand
            await this.sendBrandNotification(ticket, message, 'URGENT: Escalation Required');
            
            // Send escalation to admin
            await this.sendAdminNotification(ticket, message);
            
            // Update ticket
            await this.db.run(`
                UPDATE tickets 
                SET escalated = 1,
                    escalation_date = datetime('now'),
                    priority = 'high'
                WHERE id = ?
            `, [ticket.id]);

            // Log escalation
            await this.logFollowup(ticket.id, 'escalation', message);

            console.log(`Escalated ticket ${ticket.id}`);
        } catch (error) {
            console.error(`Error escalating ticket ${ticket.id}:`, error);
        }
    }

    // Send satisfaction surveys
    async sendSatisfactionSurveys() {
        try {
            const tickets = await this.db.all(`
                SELECT t.*, b.name as brand_name, u.email as user_email, u.full_name
                FROM tickets t
                JOIN brands b ON t.brand_id = b.id
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.status = 'resolved'
                AND t.satisfaction_survey_sent = 0
                AND t.resolved_at < datetime('now', '-${this.followupConfig.satisfactionSurveyDelay} hours')
            `);

            for (const ticket of tickets) {
                await this.sendSatisfactionSurvey(ticket);
            }

            console.log(`Sent ${tickets.length} satisfaction surveys`);
        } catch (error) {
            console.error('Satisfaction survey error:', error);
        }
    }

    // Send satisfaction survey
    async sendSatisfactionSurvey(ticket) {
        try {
            const surveyMessage = this.generateSatisfactionSurvey(ticket);
            
            // Send to user
            await this.sendUserNotification(ticket, surveyMessage, 'How was your experience?');
            
            // Update ticket
            await this.db.run(`
                UPDATE tickets 
                SET satisfaction_survey_sent = 1,
                    survey_sent_date = datetime('now')
                WHERE id = ?
            `, [ticket.id]);

            console.log(`Sent satisfaction survey for ticket ${ticket.id}`);
        } catch (error) {
            console.error(`Error sending satisfaction survey for ticket ${ticket.id}:`, error);
        }
    }

    // Generate AI-powered follow-up message
    async generateFollowupMessage(ticket, type) {
        try {
            const context = {
                ticketId: ticket.id,
                brandName: ticket.brand_name,
                complaintTitle: ticket.title,
                complaintDescription: ticket.description,
                daysOpen: Math.floor((Date.now() - new Date(ticket.created_at)) / (1000 * 60 * 60 * 24)),
                followupCount: ticket.followup_count || 0
            };

            let prompt = '';
            switch (type) {
                case 'initial':
                    prompt = `Generate a professional follow-up message for a complaint about ${context.brandName}. 
                    The complaint is: "${context.complaintTitle}" - "${context.complaintDescription}"
                    This is the initial follow-up after 24 hours. Be empathetic and ask for an update.`;
                    break;
                case 'reminder':
                    prompt = `Generate a reminder follow-up message for a complaint about ${context.brandName}. 
                    The complaint is: "${context.complaintTitle}" - "${context.complaintDescription}"
                    This is follow-up number ${context.followupCount + 1}. Be more urgent but still professional.`;
                    break;
                case 'escalation':
                    prompt = `Generate an escalation message for a complaint about ${context.brandName}. 
                    The complaint is: "${context.complaintTitle}" - "${context.complaintDescription}"
                    This complaint has been open for ${context.daysOpen} days and needs immediate attention.`;
                    break;
            }

            const response = await this.aiBot.generateResponse({
                messages: [{ role: 'user', content: prompt }]
            }, prompt, { score: 0, magnitude: 0 });

            return response.text;
        } catch (error) {
            console.error('Error generating follow-up message:', error);
            return this.getDefaultMessage(type, ticket);
        }
    }

    // Get default message if AI fails
    getDefaultMessage(type, ticket) {
        switch (type) {
            case 'initial':
                return `Dear ${ticket.brand_name} team,\n\nWe're following up on complaint #${ticket.id} regarding "${ticket.title}". This complaint was lodged 24 hours ago and we'd appreciate an update on the status.\n\nPlease provide an update or resolution timeline.\n\nBest regards,\nComplaintHub Team`;
            case 'reminder':
                return `Dear ${ticket.brand_name} team,\n\nThis is a reminder about complaint #${ticket.id} regarding "${ticket.title}". This complaint has been open for several days and requires your attention.\n\nPlease provide an immediate update.\n\nBest regards,\nComplaintHub Team`;
            case 'escalation':
                return `URGENT: Complaint #${ticket.id} regarding "${ticket.title}" has been escalated due to lack of response. This complaint has been open for an extended period and requires immediate attention.\n\nPlease respond within 24 hours or this will be escalated further.\n\nBest regards,\nComplaintHub Team`;
            default:
                return 'Please provide an update on this complaint.';
        }
    }

    // Generate satisfaction survey
    generateSatisfactionSurvey(ticket) {
        return `Dear ${ticket.full_name || 'Valued Customer'},

Thank you for using ComplaintHub to resolve your issue with ${ticket.brand_name}.

We hope your complaint has been resolved satisfactorily. Please take a moment to rate your experience:

📊 Rate your satisfaction (1-5 stars):
1 ⭐ - Very Dissatisfied
2 ⭐⭐ - Dissatisfied  
3 ⭐⭐⭐ - Neutral
4 ⭐⭐⭐⭐ - Satisfied
5 ⭐⭐⭐⭐⭐ - Very Satisfied

💬 Additional feedback (optional):
Please share any additional comments about your experience.

Your feedback helps us improve our service and ensures brands provide better customer support.

Thank you for choosing ComplaintHub!

Best regards,
The ComplaintHub Team`;
    }

    // Send brand notification
    async sendBrandNotification(ticket, message, subject = 'Complaint Follow-up') {
        try {
            // Send email notification
            await this.sendEmail(ticket.support_email, subject, message);
            
            // Send SMS if phone number available
            if (ticket.contact_info && ticket.contact_info.includes('phone')) {
                const phone = this.extractPhoneNumber(ticket.contact_info);
                if (phone) {
                    await this.sendSMS(phone, message);
                }
            }
        } catch (error) {
            console.error(`Error sending brand notification for ticket ${ticket.id}:`, error);
        }
    }

    // Send user notification
    async sendUserNotification(ticket, message, subject = 'Complaint Update') {
        try {
            if (ticket.user_email) {
                await this.sendEmail(ticket.user_email, subject, message);
            }
        } catch (error) {
            console.error(`Error sending user notification for ticket ${ticket.id}:`, error);
        }
    }

    // Send admin notification
    async sendAdminNotification(ticket, message) {
        try {
            const admins = await this.db.all('SELECT email FROM users WHERE role = "admin"');
            
            for (const admin of admins) {
                await this.sendEmail(admin.email, 'URGENT: Complaint Escalation', message);
            }
        } catch (error) {
            console.error(`Error sending admin notification for ticket ${ticket.id}:`, error);
        }
    }

    // Send email (placeholder - integrate with your email service)
    async sendEmail(to, subject, message) {
        // Integrate with your preferred email service (SendGrid, AWS SES, etc.)
        console.log(`Email to ${to}: ${subject} - ${message.substring(0, 100)}...`);
        
        // For now, just log the email
        await this.logNotification('email', to, subject, message);
    }

    // Send SMS (placeholder - integrate with your SMS service)
    async sendSMS(to, message) {
        // Integrate with your preferred SMS service (Twilio, AWS SNS, etc.)
        console.log(`SMS to ${to}: ${message.substring(0, 100)}...`);
        
        // For now, just log the SMS
        await this.logNotification('sms', to, 'SMS Notification', message);
    }

    // Extract phone number from contact info
    extractPhoneNumber(contactInfo) {
        const phoneRegex = /(\+?[\d\s\-\(\)]{10,})/;
        const match = contactInfo.match(phoneRegex);
        return match ? match[1].replace(/[\s\-\(\)]/g, '') : null;
    }

    // Log follow-up
    async logFollowup(ticketId, type, message) {
        try {
            await this.db.run(`
                INSERT INTO followup_logs (ticket_id, type, message, created_at)
                VALUES (?, ?, ?, datetime('now'))
            `, [ticketId, type, message]);
        } catch (error) {
            console.error('Follow-up logging error:', error);
        }
    }

    // Log notification
    async logNotification(type, recipient, subject, message) {
        try {
            await this.db.run(`
                INSERT INTO notification_logs (type, recipient, subject, message, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            `, [type, recipient, subject, message]);
        } catch (error) {
            console.error('Notification logging error:', error);
        }
    }

    // Get follow-up statistics
    async getFollowupStats(brandId = null) {
        try {
            let query = `
                SELECT 
                    COUNT(*) as total_tickets,
                    SUM(CASE WHEN followup_sent = 1 THEN 1 ELSE 0 END) as followups_sent,
                    SUM(CASE WHEN escalated = 1 THEN 1 ELSE 0 END) as escalated_tickets,
                    AVG(followup_count) as avg_followups,
                    AVG(CASE WHEN status = 'resolved' 
                        THEN (julianday(resolved_at) - julianday(created_at)) * 24 
                        ELSE NULL END) as avg_resolution_hours
                FROM tickets
            `;
            
            const params = [];
            if (brandId) {
                query += ' WHERE brand_id = ?';
                params.push(brandId);
            }

            const stats = await this.db.get(query, params);
            return stats;
        } catch (error) {
            console.error('Follow-up stats error:', error);
            return {};
        }
    }

    // Update follow-up configuration
    updateFollowupConfig(config) {
        this.followupConfig = { ...this.followupConfig, ...config };
    }

    // Get follow-up configuration
    getFollowupConfig() {
        return this.followupConfig;
    }
}

module.exports = FollowupService; 