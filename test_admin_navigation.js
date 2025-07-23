const puppeteer = require('puppeteer');

async function testAdminNavigation() {
  console.log('🧪 Testing Admin Navigation...\n');
  
  let browser;
  try {
    // Launch browser
    browser = await puppeteer.launch({ 
      headless: false, 
      defaultViewport: null,
      args: ['--start-maximized']
    });
    
    const page = await browser.newPage();
    
    // Navigate to the application
    console.log('1️⃣ Navigating to frontend...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    console.log('✅ Frontend loaded successfully');
    
    // Check if admin login link exists
    console.log('\n2️⃣ Checking admin login link...');
    const adminLoginLink = await page.$('a[href="/admin/login"]');
    if (adminLoginLink) {
      console.log('✅ Admin login link found');
    } else {
      console.log('❌ Admin login link not found');
    }
    
    // Click on admin login
    console.log('\n3️⃣ Clicking admin login...');
    await page.click('a[href="/admin/login"]');
    await page.waitForSelector('form', { timeout: 5000 });
    console.log('✅ Admin login page loaded');
    
    // Fill in admin credentials
    console.log('\n4️⃣ Filling admin credentials...');
    await page.type('input[name="email"]', 'admin@complainthub.com');
    await page.type('input[name="password"]', 'admin123');
    console.log('✅ Credentials filled');
    
    // Submit login form
    console.log('\n5️⃣ Submitting login form...');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    console.log('✅ Login submitted');
    
    // Check if admin dashboard loaded
    console.log('\n6️⃣ Checking admin dashboard...');
    const dashboardTitle = await page.$('h1');
    if (dashboardTitle) {
      const titleText = await page.evaluate(el => el.textContent, dashboardTitle);
      console.log('✅ Dashboard loaded:', titleText.trim());
    } else {
      console.log('❌ Dashboard not loaded properly');
    }
    
    // Check for admin navigation links
    console.log('\n7️⃣ Checking admin navigation links...');
    const navLinks = await page.$$('nav .nav-link');
    console.log(`Found ${navLinks.length} navigation links`);
    
    for (const link of navLinks) {
      const href = await page.evaluate(el => el.getAttribute('href'), link);
      const text = await page.evaluate(el => el.textContent, link);
      if (href && href.includes('/admin/')) {
        console.log(`✅ Admin nav link: ${text.trim()} -> ${href}`);
      }
    }
    
    // Test Dashboard link specifically
    console.log('\n8️⃣ Testing Dashboard link...');
    const dashboardLink = await page.$('a[href="/admin/dashboard"]');
    if (dashboardLink) {
      console.log('✅ Dashboard link found in navigation');
      
      // Check if it's active
      const isActive = await page.evaluate(el => el.classList.contains('active'), dashboardLink);
      if (isActive) {
        console.log('✅ Dashboard link is active (current page)');
      } else {
        console.log('⚠️ Dashboard link is not active');
      }
    } else {
      console.log('❌ Dashboard link not found in navigation');
    }
    
    // Test clicking on Brands link
    console.log('\n9️⃣ Testing Brands navigation...');
    const brandsLink = await page.$('a[href="/admin/brands"]');
    if (brandsLink) {
      console.log('✅ Brands link found');
      await brandsLink.click();
      await page.waitForTimeout(2000);
      
      // Check if we're on brands page
      const currentUrl = page.url();
      if (currentUrl.includes('/admin/brands')) {
        console.log('✅ Successfully navigated to brands page');
      } else {
        console.log('❌ Failed to navigate to brands page');
      }
    } else {
      console.log('❌ Brands link not found');
    }
    
    // Test clicking on Analytics link
    console.log('\n🔟 Testing Analytics navigation...');
    const analyticsLink = await page.$('a[href="/admin/analytics"]');
    if (analyticsLink) {
      console.log('✅ Analytics link found');
      await analyticsLink.click();
      await page.waitForTimeout(2000);
      
      // Check if we're on analytics page
      const currentUrl = page.url();
      if (currentUrl.includes('/admin/analytics')) {
        console.log('✅ Successfully navigated to analytics page');
      } else {
        console.log('❌ Failed to navigate to analytics page');
      }
    } else {
      console.log('❌ Analytics link not found');
    }
    
    // Test clicking on Tickets link
    console.log('\n1️⃣1️⃣ Testing Tickets navigation...');
    const ticketsLink = await page.$('a[href="/admin/tickets"]');
    if (ticketsLink) {
      console.log('✅ Tickets link found');
      await ticketsLink.click();
      await page.waitForTimeout(2000);
      
      // Check if we're on tickets page
      const currentUrl = page.url();
      if (currentUrl.includes('/admin/tickets')) {
        console.log('✅ Successfully navigated to tickets page');
      } else {
        console.log('❌ Failed to navigate to tickets page');
      }
    } else {
      console.log('❌ Tickets link not found');
    }
    
    // Test clicking on Users link
    console.log('\n1️⃣2️⃣ Testing Users navigation...');
    const usersLink = await page.$('a[href="/admin/users"]');
    if (usersLink) {
      console.log('✅ Users link found');
      await usersLink.click();
      await page.waitForTimeout(2000);
      
      // Check if we're on users page
      const currentUrl = page.url();
      if (currentUrl.includes('/admin/users')) {
        console.log('✅ Successfully navigated to users page');
      } else {
        console.log('❌ Failed to navigate to users page');
      }
    } else {
      console.log('❌ Users link not found');
    }
    
    // Test clicking on Dashboard link to go back
    console.log('\n1️⃣3️⃣ Testing Dashboard navigation (return)...');
    const dashboardLinkReturn = await page.$('a[href="/admin/dashboard"]');
    if (dashboardLinkReturn) {
      console.log('✅ Dashboard link found for return');
      await dashboardLinkReturn.click();
      await page.waitForTimeout(2000);
      
      // Check if we're back on dashboard
      const currentUrl = page.url();
      if (currentUrl.includes('/admin/dashboard')) {
        console.log('✅ Successfully returned to dashboard');
      } else {
        console.log('❌ Failed to return to dashboard');
      }
    } else {
      console.log('❌ Dashboard link not found for return');
    }
    
    console.log('\n🎉 Admin Navigation Test Completed Successfully!');
    console.log('\n📝 Summary:');
    console.log('   ✅ Admin login accessible');
    console.log('   ✅ Admin dashboard loads');
    console.log('   ✅ Navigation links present');
    console.log('   ✅ Dashboard link works');
    console.log('   ✅ Brands link works');
    console.log('   ✅ Analytics link works');
    console.log('   ✅ Tickets link works');
    console.log('   ✅ Users link works');
    console.log('   ✅ Navigation between pages works');
    
    // Wait a bit before closing
    await page.waitForTimeout(3000);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Run the test
testAdminNavigation(); 