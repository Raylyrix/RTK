// Test script to verify all required modules are available
console.log('🧪 Testing RTX Innovations dependencies...');

// Test if all required modules are available
const modules = [
  'electron-store',
  'googleapis', 
  'node-cron',
  'mime-types',
  'xlsx',
  'csv-parser',
  'moment'
];

let allModulesLoaded = true;

modules.forEach(moduleName => {
  try {
    require(moduleName);
    console.log(`✅ ${moduleName} loaded successfully`);
  } catch (error) {
    console.error(`❌ Error loading ${moduleName}:`, error.message);
    allModulesLoaded = false;
  }
});

// Test electron-is-dev separately (only works in Electron environment)
try {
  require('electron-is-dev');
  console.log('✅ electron-is-dev loaded successfully');
} catch (error) {
  console.log('⚠️  electron-is-dev: Not running in Electron environment (expected)');
}

// Test if the build files exist
const fs = require('fs');
const path = require('path');

const requiredFiles = [
  'dist/index.html',
  'dist/bundle.js',
  'src/main.js',
  'src/preload.js'
];

console.log('\n📁 Checking required files...');
requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file} exists`);
  } else {
    console.error(`❌ ${file} missing`);
    allModulesLoaded = false;
  }
});

if (allModulesLoaded) {
  console.log('\n✅ All tests passed! The application should work properly.');
  console.log('You can now run: npm run dev-simple');
} else {
  console.log('\n❌ Some tests failed. Please check the errors above.');
  process.exit(1);
} 