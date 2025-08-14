// Simple test script to verify the app is working
console.log('🧪 Testing AutoMailer Pro...');

// Test DOM access
if (typeof document !== 'undefined') {
    console.log('✅ DOM is available');
    
    // Test if our elements exist
    const loginBtn = document.getElementById('loginBtn');
    const connectSheetsBtn = document.getElementById('connectSheetsBtn');
    const campaignName = document.getElementById('campaignName');
    
    console.log('Login button found:', !!loginBtn);
    console.log('Connect sheets button found:', !!connectSheetsBtn);
    console.log('Campaign name input found:', !!campaignName);
    
    // Test if our app is initialized
    if (window.rtxApp) {
        console.log('✅ RTX App is initialized');
        console.log('App authenticated:', window.rtxApp.isAuthenticated);
    } else {
        console.log('❌ RTX App not found');
    }
} else {
    console.log('❌ DOM not available');
}

console.log('�� Test complete'); 