const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY || 'your-stripe-key');
const cron = require('node-cron');

class BillingService {
    constructor(db) {
        this.db = db;
        this.stripe = stripe;
        
        // Initialize billing rules
        this.billingRules = {
            complaintFee: 5.00, // $5 per complaint
            monthlySubscription: 29.99, // $29.99/month for brands
            creditThreshold: 10.00, // Minimum credit balance
            autoRecharge: true,
            rechargeAmount: 50.00 // Auto-recharge amount
        };

        // Setup automated billing tasks
        this.setupAutomatedBilling();
    }

    // Setup automated billing tasks
    setupAutomatedBilling() {
        // Daily credit check and auto-recharge
        cron.schedule('0 9 * * *', async () => {
            await this.checkLowCredits();
        });

        // Monthly subscription billing
        cron.schedule('0 0 1 * *', async () => {
            await this.processMonthlySubscriptions();
        });

        // 24-hour rule enforcement
        cron.schedule('0 */6 * * *', async () => {
            await this.enforce24HourRule();
        });
    }

    // Get brand credit balance
    async getBrandCredits(brandId) {
        try {
            const brand = await this.db.get('SELECT credit_balance FROM brands WHERE id = ?', [brandId]);
            return brand ? brand.credit_balance : 0;
        } catch (error) {
            console.error('Error getting brand credits:', error);
            return 0;
        }
    }

    // Deduct credits for complaint processing
    async deductCredits(brandId, amount = this.billingRules.complaintFee) {
        try {
            const currentBalance = await this.getBrandCredits(brandId);
            
            if (currentBalance < amount) {
                throw new Error('Insufficient credits');
            }

            const newBalance = currentBalance - amount;
            
            await this.db.run(
                'UPDATE brands SET credit_balance = ? WHERE id = ?',
                [newBalance, brandId]
            );

            // Log the transaction
            await this.logTransaction(brandId, 'deduction', amount, 'Complaint processing fee');

            return {
                success: true,
                previousBalance: currentBalance,
                newBalance: newBalance,
                deducted: amount
            };

        } catch (error) {
            console.error('Error deducting credits:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Add credits to brand account
    async addCredits(brandId, amount, reason = 'Manual credit addition') {
        try {
            const currentBalance = await this.getBrandCredits(brandId);
            const newBalance = currentBalance + amount;
            
            await this.db.run(
                'UPDATE brands SET credit_balance = ? WHERE id = ?',
                [newBalance, brandId]
            );

            // Log the transaction
            await this.logTransaction(brandId, 'addition', amount, reason);

            return {
                success: true,
                previousBalance: currentBalance,
                newBalance: newBalance,
                added: amount
            };

        } catch (error) {
            console.error('Error adding credits:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Process payment and add credits
    async processPayment(brandId, amount, paymentMethodId) {
        try {
            // Get brand information
            const brand = await this.db.get('SELECT * FROM brands WHERE id = ?', [brandId]);
            if (!brand) {
                throw new Error('Brand not found');
            }

            // Create payment intent with Stripe
            const paymentIntent = await this.stripe.paymentIntents.create({
                amount: Math.round(amount * 100), // Convert to cents
                currency: 'usd',
                payment_method: paymentMethodId,
                confirm: true,
                description: `Credit purchase for ${brand.name}`,
                metadata: {
                    brandId: brandId,
                    brandName: brand.name
                }
            });

            if (paymentIntent.status === 'succeeded') {
                // Add credits to brand account
                const result = await this.addCredits(brandId, amount, 'Credit purchase');
                
                if (result.success) {
                    // Log successful payment
                    await this.logPayment(brandId, paymentIntent.id, amount, 'success');
                    
                    return {
                        success: true,
                        paymentIntentId: paymentIntent.id,
                        creditsAdded: amount,
                        newBalance: result.newBalance
                    };
                } else {
                    throw new Error('Failed to add credits after payment');
                }
            } else {
                throw new Error(`Payment failed: ${paymentIntent.status}`);
            }

        } catch (error) {
            console.error('Payment processing error:', error);
            
            // Log failed payment
            await this.logPayment(brandId, null, amount, 'failed', error.message);
            
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Create subscription for brand
    async createSubscription(brandId, planId = 'monthly_basic') {
        try {
            const brand = await this.db.get('SELECT * FROM brands WHERE id = ?', [brandId]);
            if (!brand) {
                throw new Error('Brand not found');
            }

            // Create customer in Stripe if not exists
            let customerId = brand.stripe_customer_id;
            if (!customerId) {
                const customer = await this.stripe.customers.create({
                    email: brand.support_email,
                    name: brand.name,
                    metadata: {
                        brandId: brandId
                    }
                });
                
                customerId = customer.id;
                
                // Update brand with customer ID
                await this.db.run(
                    'UPDATE brands SET stripe_customer_id = ? WHERE id = ?',
                    [customerId, brandId]
                );
            }

            // Create subscription
            const subscription = await this.stripe.subscriptions.create({
                customer: customerId,
                items: [{ price: this.getPlanPriceId(planId) }],
                metadata: {
                    brandId: brandId,
                    brandName: brand.name
                }
            });

            // Update brand subscription info
            await this.db.run(
                'UPDATE brands SET stripe_subscription_id = ?, subscription_status = ? WHERE id = ?',
                [subscription.id, subscription.status, brandId]
            );

            return {
                success: true,
                subscriptionId: subscription.id,
                status: subscription.status
            };

        } catch (error) {
            console.error('Subscription creation error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Cancel subscription
    async cancelSubscription(brandId) {
        try {
            const brand = await this.db.get('SELECT stripe_subscription_id FROM brands WHERE id = ?', [brandId]);
            if (!brand || !brand.stripe_subscription_id) {
                throw new Error('No active subscription found');
            }

            // Cancel subscription in Stripe
            const subscription = await this.stripe.subscriptions.update(
                brand.stripe_subscription_id,
                { cancel_at_period_end: true }
            );

            // Update brand subscription status
            await this.db.run(
                'UPDATE brands SET subscription_status = ? WHERE id = ?',
                ['canceling', brandId]
            );

            return {
                success: true,
                subscriptionId: subscription.id,
                status: subscription.status
            };

        } catch (error) {
            console.error('Subscription cancellation error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Check for low credits and auto-recharge
    async checkLowCredits() {
        try {
            const brands = await this.db.all(
                'SELECT id, name, credit_balance, stripe_customer_id, auto_recharge FROM brands WHERE credit_balance < ? AND auto_recharge = 1',
                [this.billingRules.creditThreshold]
            );

            for (const brand of brands) {
                if (brand.stripe_customer_id) {
                    await this.autoRecharge(brand.id, brand.stripe_customer_id);
                }
            }

            console.log(`Checked ${brands.length} brands for low credits`);
        } catch (error) {
            console.error('Low credit check error:', error);
        }
    }

    // Auto-recharge brand account
    async autoRecharge(brandId, customerId) {
        try {
            // Get default payment method
            const paymentMethods = await this.stripe.paymentMethods.list({
                customer: customerId,
                type: 'card'
            });

            if (paymentMethods.data.length > 0) {
                const paymentMethod = paymentMethods.data[0];
                
                // Process auto-recharge
                const result = await this.processPayment(
                    brandId, 
                    this.billingRules.rechargeAmount, 
                    paymentMethod.id
                );

                if (result.success) {
                    console.log(`Auto-recharged ${brandId} with $${this.billingRules.rechargeAmount}`);
                }
            }
        } catch (error) {
            console.error(`Auto-recharge error for brand ${brandId}:`, error);
        }
    }

    // Process monthly subscriptions
    async processMonthlySubscriptions() {
        try {
            const subscriptions = await this.db.all(
                'SELECT id, stripe_subscription_id FROM brands WHERE subscription_status = "active"'
            );

            for (const brand of subscriptions) {
                try {
                    const subscription = await this.stripe.subscriptions.retrieve(
                        brand.stripe_subscription_id
                    );

                    if (subscription.status === 'active') {
                        // Add monthly credits
                        await this.addCredits(
                            brand.id, 
                            this.billingRules.monthlySubscription, 
                            'Monthly subscription credits'
                        );
                    }
                } catch (error) {
                    console.error(`Error processing subscription for brand ${brand.id}:`, error);
                }
            }
        } catch (error) {
            console.error('Monthly subscription processing error:', error);
        }
    }

    // Enforce 24-hour rule
    async enforce24HourRule() {
        try {
            const tickets = await this.db.all(`
                SELECT t.id, t.brand_id, t.created_at, t.status 
                FROM tickets t 
                WHERE t.status = 'open' 
                AND t.created_at < datetime('now', '-24 hours')
            `);

            for (const ticket of tickets) {
                // Charge brand for unresolved ticket
                const result = await this.deductCredits(ticket.brand_id, this.billingRules.complaintFee);
                
                if (result.success) {
                    // Update ticket status
                    await this.db.run(
                        'UPDATE tickets SET status = ? WHERE id = ?',
                        ['charged', ticket.id]
                    );

                    console.log(`Charged brand ${ticket.brand_id} for unresolved ticket ${ticket.id}`);
                }
            }
        } catch (error) {
            console.error('24-hour rule enforcement error:', error);
        }
    }

    // Log transaction
    async logTransaction(brandId, type, amount, reason) {
        try {
            await this.db.run(`
                INSERT INTO billing_transactions (brand_id, type, amount, reason, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            `, [brandId, type, amount, reason]);
        } catch (error) {
            console.error('Transaction logging error:', error);
        }
    }

    // Log payment
    async logPayment(brandId, paymentIntentId, amount, status, errorMessage = null) {
        try {
            await this.db.run(`
                INSERT INTO payment_logs (brand_id, payment_intent_id, amount, status, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            `, [brandId, paymentIntentId, amount, status, errorMessage]);
        } catch (error) {
            console.error('Payment logging error:', error);
        }
    }

    // Get billing history
    async getBillingHistory(brandId, limit = 50) {
        try {
            const transactions = await this.db.all(`
                SELECT * FROM billing_transactions 
                WHERE brand_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            `, [brandId, limit]);

            const payments = await this.db.all(`
                SELECT * FROM payment_logs 
                WHERE brand_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            `, [brandId, limit]);

            return {
                transactions,
                payments
            };
        } catch (error) {
            console.error('Billing history error:', error);
            return { transactions: [], payments: [] };
        }
    }

    // Get plan price ID
    getPlanPriceId(planId) {
        const plans = {
            'monthly_basic': process.env.STRIPE_MONTHLY_BASIC_PRICE_ID || 'price_basic',
            'monthly_premium': process.env.STRIPE_MONTHLY_PREMIUM_PRICE_ID || 'price_premium',
            'yearly_basic': process.env.STRIPE_YEARLY_BASIC_PRICE_ID || 'price_yearly_basic'
        };
        return plans[planId] || plans['monthly_basic'];
    }

    // Update billing rules
    updateBillingRules(rules) {
        this.billingRules = { ...this.billingRules, ...rules };
    }

    // Get billing rules
    getBillingRules() {
        return this.billingRules;
    }
}

module.exports = BillingService; 