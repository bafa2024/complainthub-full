// Test script to create sample data and test brand manager functionality
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const path = require('path');

const JWT_SECRET = 'your-secret-key-change-in-production';
const dbPath = path.join(__dirname, 'backend-nodejs', 'voicebot.db');

console.log('🔧 Setting up test data for brand manager functionality...\n');

// Helper function to run database queries
function runQuery(db, query, params = []) {
  return new Promise((resolve, reject) => {
    db.run(query, params, function(err) {
      if (err) reject(err);
      else resolve(this);
    });
  });
}

function getQuery(db, query, params = []) {
  return new Promise((resolve, reject) => {
    db.get(query, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

function allQuery(db, query, params = []) {
  return new Promise((resolve, reject) => {
    db.all(query, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

async function setupTestData() {
  const db = new sqlite3.Database(dbPath);

  try {
    console.log('1. Creating brand manager user...');
    
    // Hash password for brand manager
    const hashedPassword = await bcrypt.hash('password123', 10);
    
    // Create brand manager user
    try {
      await runQuery(db, `
        INSERT OR REPLACE INTO users (id, email, full_name, hashed_password, role, brand_id)
        VALUES (10, 'brandmanager@test.com', 'Brand Manager Test', ?, 'brand_user', 1)
      `, [hashedPassword]);
      console.log('   ✅ Brand manager user created');
    } catch (err) {
      console.log('   ⚠️  User may already exist:', err.message);
    }

    console.log('\n2. Creating test brand...');
    
    // Create test brand
    try {
      await runQuery(db, `
        INSERT OR REPLACE INTO brands (id, name, description, support_email, industry, user_id, credit_balance)
        VALUES (1, 'Test Brand Co', 'A test brand for testing', 'brandmanager@test.com', 'Technology', 10, 100.0)
      `);
      console.log('   ✅ Test brand created');
    } catch (err) {
      console.log('   ⚠️  Brand may already exist:', err.message);
    }

    console.log('\n3. Creating test tickets for the brand...');
    
    // Create test tickets
    const tickets = [
      {
        title: 'Product quality complaint',
        description: 'The product I received was damaged',
        status: 'new',
        priority: 'high',
        category: 'complaint',
        user_id: 1,
        brand_id: 1
      },
      {
        title: 'Service delivery issue',
        description: 'Late delivery of service',
        status: 'in-progress',
        priority: 'medium',
        category: 'complaint',
        user_id: 2,
        brand_id: 1
      },
      {
        title: 'Billing inquiry',
        description: 'Question about recent charges',
        status: 'resolved',
        priority: 'low',
        category: 'inquiry',
        user_id: 1,
        brand_id: 1
      }
    ];

    for (let i = 0; i < tickets.length; i++) {
      const ticket = tickets[i];
      try {
        await runQuery(db, `
          INSERT OR REPLACE INTO tickets (id, title, description, status, priority, category, user_id, brand_id)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `, [i + 100, ticket.title, ticket.description, ticket.status, ticket.priority, ticket.category, ticket.user_id, ticket.brand_id]);
      } catch (err) {
        console.log(`   ⚠️  Ticket ${i + 1} may already exist:`, err.message);
      }
    }
    console.log('   ✅ Test tickets created');

    console.log('\n4. Generating test JWT token...');
    
    // Generate JWT token for testing
    const token = jwt.sign({
      user_id: 10,
      email: 'brandmanager@test.com',
      role: 'brand_user',
      brand_id: 1
    }, JWT_SECRET);
    
    console.log('   ✅ JWT Token generated:');
    console.log('   ', token);

    console.log('\n5. Verifying data...');
    
    // Verify brand manager
    const user = await getQuery(db, 'SELECT * FROM users WHERE id = 10');
    if (user) {
      console.log(`   ✅ Brand manager: ${user.full_name} (${user.email})`);
    }
    
    // Verify brand
    const brand = await getQuery(db, 'SELECT * FROM brands WHERE id = 1');
    if (brand) {
      console.log(`   ✅ Brand: ${brand.name} (${brand.support_email})`);
    }
    
    // Verify tickets
    const ticketCount = await getQuery(db, 'SELECT COUNT(*) as count FROM tickets WHERE brand_id = 1');
    console.log(`   ✅ Tickets for brand: ${ticketCount.count}`);

    console.log('\n📋 Test Setup Complete!');
    console.log('\nNext steps:');
    console.log('1. Restart the backend server to pick up the new /api/v1/brands/:id/tickets endpoint');
    console.log('2. Login with: brandmanager@test.com / password123');
    console.log('3. Navigate to Brand Dashboard to see tickets');
    console.log('4. Navigate to My Brands to see brand list');

  } catch (error) {
    console.error('❌ Error setting up test data:', error);
  } finally {
    db.close();
  }
}

setupTestData();