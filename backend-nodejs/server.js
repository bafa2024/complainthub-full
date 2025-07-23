const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8001;
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

// Middleware
app.use(cors({
  origin: ['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174'],
  credentials: true
}));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Database setup
const dbPath = path.join(__dirname, 'voicebot.db');
const db = new sqlite3.Database(dbPath);

// Initialize database tables
db.serialize(() => {
  // Users table (simplified - no brand_id to avoid circular dependency)
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  // Brands table
  db.run(`CREATE TABLE IF NOT EXISTS brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    user_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  // Tickets table
  db.run(`CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    priority TEXT DEFAULT 'medium',
    user_id INTEGER,
    brand_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
});

// Helper function to run database queries
function runQuery(query, params = []) {
  return new Promise((resolve, reject) => {
    db.run(query, params, function(err) {
      if (err) reject(err);
      else resolve({ id: this.lastID, changes: this.changes });
    });
  });
}

function getQuery(query, params = []) {
  return new Promise((resolve, reject) => {
    db.get(query, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

function allQuery(query, params = []) {
  return new Promise((resolve, reject) => {
    db.all(query, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

// Authentication middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
}

// Health check endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'ComplaintHub Backend API', 
    status: 'running',
    timestamp: new Date().toISOString()
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// Signup endpoint
app.post('/api/v1/auth/signup', async (req, res) => {
  try {
    console.log('🔍 Signup request received:', req.body);
    const { email, full_name, password, brand_name, role = 'user' } = req.body;

    if (!email || !full_name || !password) {
      return res.status(400).json({ 
        error: 'Email, full_name, and password are required' 
      });
    }

    // Check if user already exists
    const existingUser = await getQuery('SELECT * FROM users WHERE email = ?', [email]);
    if (existingUser) {
      return res.status(400).json({ error: 'User already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);
    console.log('✅ Password hashed successfully');

    // Create user
    console.log('📝 Creating user with role:', role);
    const result = await runQuery(
      'INSERT INTO users (email, full_name, hashed_password, role) VALUES (?, ?, ?, ?)',
      [email, full_name, hashedPassword, role]
    );
    console.log('✅ User created with ID:', result.id);

    // Get the created user
    let user = await getQuery('SELECT id, email, full_name, role FROM users WHERE id = ?', [result.id]);
    console.log('✅ User retrieved:', user);

    // If this is a brand signup, create the brand
    let brand = null;
    if (brand_name && role === 'brand_user') {
      console.log('🏢 Creating brand:', brand_name);
      try {
        const brandResult = await runQuery(
          'INSERT INTO brands (name, description, user_id) VALUES (?, ?, ?)',
          [brand_name, `Brand created by ${full_name}`, user.id]
        );
        console.log('✅ Brand created with ID:', brandResult.id);
        
        brand = await getQuery('SELECT * FROM brands WHERE id = ?', [brandResult.id]);
        console.log('✅ Brand retrieved:', brand);
      } catch (brandError) {
        console.error('❌ Brand creation error:', brandError);
        throw brandError;
      }
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        user_id: user.id, 
        email: user.email, 
        role: user.role 
      }, 
      JWT_SECRET, 
      { expiresIn: '24h' }
    );
    console.log('✅ JWT token generated');

    const response = {
      access_token: token,
      token_type: 'bearer',
      user: {
        id: user.id,
        email: user.email,
        full_name: user.full_name,
        role: user.role,
        brand: brand
      }
    };
    
    console.log('✅ Signup successful, sending response');
    res.status(201).json(response);

  } catch (error) {
    console.error('❌ Signup error:', error);
    console.error('❌ Error stack:', error.stack);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Login endpoint
app.post('/api/v1/login/access-token', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ 
        error: 'Username and password are required' 
      });
    }

    // Find user by email (username)
    const user = await getQuery('SELECT * FROM users WHERE email = ?', [username]);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Check password
    const validPassword = await bcrypt.compare(password, user.hashed_password);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        user_id: user.id, 
        email: user.email, 
        role: user.role 
      }, 
      JWT_SECRET, 
      { expiresIn: '24h' }
    );

    res.json({
      access_token: token,
      token_type: 'bearer',
      user: {
        id: user.id,
        email: user.email,
        full_name: user.full_name,
        role: user.role
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get current user endpoint
app.get('/api/v1/users/me', authenticateToken, async (req, res) => {
  try {
    const user = await getQuery(
      'SELECT id, email, full_name, role, created_at FROM users WHERE id = ?', 
      [req.user.user_id]
    );

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      id: user.id,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      created_at: user.created_at
    });

  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all users (admin only)
app.get('/api/v1/users', authenticateToken, async (req, res) => {
  try {
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const users = await allQuery(
      'SELECT id, email, full_name, role, created_at FROM users'
    );

    res.json(users);

  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create brand endpoint
app.post('/api/v1/brands', authenticateToken, async (req, res) => {
  try {
    const { name, description } = req.body;

    if (!name) {
      return res.status(400).json({ error: 'Brand name is required' });
    }

    const result = await runQuery(
      'INSERT INTO brands (name, description, user_id) VALUES (?, ?, ?)',
      [name, description, req.user.user_id]
    );

    const brand = await getQuery('SELECT * FROM brands WHERE id = ?', [result.id]);

    res.status(201).json(brand);

  } catch (error) {
    console.error('Create brand error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get user's brands
app.get('/api/v1/brands', authenticateToken, async (req, res) => {
  try {
    const brands = await allQuery(
      'SELECT * FROM brands WHERE user_id = ?',
      [req.user.user_id]
    );

    res.json(brands);

  } catch (error) {
    console.error('Get brands error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create ticket endpoint
app.post('/api/v1/tickets', authenticateToken, async (req, res) => {
  try {
    const { title, description, brand_id, priority } = req.body;

    if (!title) {
      return res.status(400).json({ error: 'Ticket title is required' });
    }

    const result = await runQuery(
      'INSERT INTO tickets (title, description, brand_id, user_id, priority) VALUES (?, ?, ?, ?, ?)',
      [title, description, brand_id, req.user.user_id, priority || 'medium']
    );

    const ticket = await getQuery('SELECT * FROM tickets WHERE id = ?', [result.id]);

    res.status(201).json(ticket);

  } catch (error) {
    console.error('Create ticket error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Public ticket creation endpoint (no authentication required)
app.post('/api/v1/public/tickets', async (req, res) => {
  try {
    console.log('🔍 Public ticket creation request received:', req.body);
    const { 
      fullName, 
      email, 
      phone, 
      brandName, 
      title, 
      description, 
      category, 
      priority = 'medium',
      isAnonymous = false 
    } = req.body;

    // Validation
    if (!fullName || !email || !brandName || !title || !description || !category) {
      return res.status(400).json({ 
        error: 'Full name, email, brand name, title, description, and category are required' 
      });
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ error: 'Invalid email format' });
    }

    // First, check if brand exists, if not create it
    let brand = await getQuery('SELECT * FROM brands WHERE name = ?', [brandName]);
    if (!brand) {
      console.log('🏢 Creating new brand:', brandName);
      const brandResult = await runQuery(
        'INSERT INTO brands (name, description) VALUES (?, ?)',
        [brandName, `Brand created from public complaint`]
      );
      brand = await getQuery('SELECT * FROM brands WHERE id = ?', [brandResult.id]);
      console.log('✅ Brand created with ID:', brand.id);
    }

    // Create or find user (for anonymous complaints, create a temporary user)
    let user = await getQuery('SELECT * FROM users WHERE email = ?', [email]);
    if (!user) {
      console.log('👤 Creating new user for public complaint');
      const hashedPassword = await bcrypt.hash(Math.random().toString(36), 10); // Temporary password
      const userResult = await runQuery(
        'INSERT INTO users (email, full_name, hashed_password, role) VALUES (?, ?, ?, ?)',
        [email, fullName, hashedPassword, 'user']
      );
      user = await getQuery('SELECT * FROM users WHERE id = ?', [userResult.id]);
      console.log('✅ User created with ID:', user.id);
    }

    // Create the ticket
    console.log('📝 Creating public ticket');
    const ticketResult = await runQuery(
      'INSERT INTO tickets (title, description, brand_id, user_id, priority, status) VALUES (?, ?, ?, ?, ?, ?)',
      [title, description, brand.id, user.id, priority, 'open']
    );

    const ticket = await getQuery('SELECT * FROM tickets WHERE id = ?', [ticketResult.id]);
    console.log('✅ Ticket created with ID:', ticket.id);

    // Generate ticket number
    const ticketNumber = `TKT-${String(ticket.id).padStart(6, '0')}`;

    // Prepare response
    const response = {
      ticket_number: ticketNumber,
      ticket_id: ticket.id,
      status: 'open',
      message: 'Complaint submitted successfully',
      submitted_at: new Date().toISOString(),
      brand_name: brand.name,
      category: category,
      priority: priority
    };

    console.log('✅ Public ticket creation successful, sending response');
    res.status(201).json(response);

  } catch (error) {
    console.error('❌ Public ticket creation error:', error);
    console.error('❌ Error stack:', error.stack);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Get user's tickets
app.get('/api/v1/tickets', authenticateToken, async (req, res) => {
  try {
    const tickets = await allQuery(
      'SELECT t.*, b.name as brand_name FROM tickets t LEFT JOIN brands b ON t.brand_id = b.id WHERE t.user_id = ?',
      [req.user.user_id]
    );

    res.json(tickets);

  } catch (error) {
    console.error('Get tickets error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all tickets (admin only)
app.get('/api/v1/admin/tickets', authenticateToken, async (req, res) => {
  try {
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const tickets = await allQuery(
      'SELECT t.*, b.name as brand_name, u.email as user_email, u.full_name as user_name FROM tickets t LEFT JOIN brands b ON t.brand_id = b.id LEFT JOIN users u ON t.user_id = u.id'
    );

    res.json(tickets);

  } catch (error) {
    console.error('Get admin tickets error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update ticket status
app.put('/api/v1/tickets/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const { status, priority } = req.body;

    const ticket = await getQuery('SELECT * FROM tickets WHERE id = ?', [id]);
    if (!ticket) {
      return res.status(404).json({ error: 'Ticket not found' });
    }

    // Check if user owns the ticket or is admin
    if (ticket.user_id !== req.user.user_id && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Access denied' });
    }

    await runQuery(
      'UPDATE tickets SET status = ?, priority = ? WHERE id = ?',
      [status || ticket.status, priority || ticket.priority, id]
    );

    const updatedTicket = await getQuery('SELECT * FROM tickets WHERE id = ?', [id]);
    res.json(updatedTicket);

  } catch (error) {
    console.error('Update ticket error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Admin endpoints
app.get('/api/v1/admin/brands', authenticateToken, async (req, res) => {
  try {
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const brands = await allQuery('SELECT * FROM brands');
    res.json(brands);

  } catch (error) {
    console.error('Get admin brands error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/v1/admin/brands', authenticateToken, async (req, res) => {
  try {
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const { name, description } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Brand name is required' });
    }

    const result = await runQuery(
      'INSERT INTO brands (name, description, user_id) VALUES (?, ?, ?)',
      [name, description, req.user.user_id]
    );

    const brand = await getQuery('SELECT * FROM brands WHERE id = ?', [result.id]);
    res.status(201).json(brand);

  } catch (error) {
    console.error('Create admin brand error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Brand-specific endpoints
app.get('/api/v1/brand/dashboard', authenticateToken, async (req, res) => {
  try {
    if (req.user.role !== 'brand_user') {
      return res.status(403).json({ error: 'Brand user access required' });
    }

    // Get user's brand
    const brand = await getQuery('SELECT * FROM brands WHERE user_id = ?', [req.user.user_id]);
    if (!brand) {
      return res.status(404).json({ error: 'Brand not found' });
    }

    // Get brand's tickets
    const tickets = await allQuery(
      'SELECT t.*, u.email as user_email, u.full_name as user_name FROM tickets t LEFT JOIN users u ON t.user_id = u.id WHERE t.brand_id = ?',
      [brand.id]
    );

    res.json({
      brand,
      tickets,
      stats: {
        total_tickets: tickets.length,
        open_tickets: tickets.filter(t => t.status === 'open').length,
        closed_tickets: tickets.filter(t => t.status === 'closed').length
      }
    });

  } catch (error) {
    console.error('Get brand dashboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// User dashboard endpoint
app.get('/api/v1/user/dashboard', authenticateToken, async (req, res) => {
  try {
    const user = await getQuery(
      'SELECT id, email, full_name, role, created_at FROM users WHERE id = ?', 
      [req.user.user_id]
    );

    const tickets = await allQuery(
      'SELECT t.*, b.name as brand_name FROM tickets t LEFT JOIN brands b ON t.brand_id = b.id WHERE t.user_id = ?',
      [req.user.user_id]
    );

    res.json({
      user,
      tickets,
      stats: {
        total_tickets: tickets.length,
        open_tickets: tickets.filter(t => t.status === 'open').length,
        closed_tickets: tickets.filter(t => t.status === 'closed').length
      }
    });

  } catch (error) {
    console.error('Get user dashboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🔐 API base: http://localhost:${PORT}/api/v1`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down server...');
  db.close((err) => {
    if (err) {
      console.error('Error closing database:', err);
    } else {
      console.log('✅ Database connection closed');
    }
    process.exit(0);
  });
}); 