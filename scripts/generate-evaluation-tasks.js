#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('http');

// Configuration
const API_HOST = process.env.API_HOST || 'http://localhost:8000';
const NUM_TASKS = process.argv[2] || 3;
const OUTPUT_DIR = process.argv[3] || './evaluation_tasks';

// Colors
const colors = {
  green: '\x1b[0;32m',
  red: '\x1b[0;31m',
  yellow: '\x1b[1;33m',
  reset: '\x1b[0m'
};

function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Create output directory
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Generate timestamp
const timestamp = new Date()
  .toISOString()
  .replace(/[-:]/g, '')
  .replace('T', '_')
  .split('.')[0];
const outputFile = path.join(OUTPUT_DIR, `tasks_${timestamp}.json`);

log('yellow', 'Generating evaluation tasks...');
console.log(`API Host: ${API_HOST}`);
console.log(`Number of tasks: ${NUM_TASKS}`);
console.log(`Output directory: ${OUTPUT_DIR}`);

// Parse URL
const url = new URL(`${API_HOST}/api/generate-evaluation-tasks?num_tasks=${NUM_TASKS}`);
const httpModule = url.protocol === 'https:' ? require('https') : require('http');

// Make API request
const req = httpModule.get(url, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    if (res.statusCode === 200) {
      // Write to file
      fs.writeFileSync(outputFile, data, 'utf8');

      log('green', '✓ Success!');
      console.log(`Tasks saved to: ${outputFile}`);

      // Pretty print
      log('yellow', '\nPreview:');
      try {
        const jsonData = JSON.parse(data);
        console.log(JSON.stringify(jsonData, null, 2));
      } catch (e) {
        console.log(data);
      }

      process.exit(0);
    } else {
      log('red', `✗ Error: API returned HTTP ${res.statusCode}`);
      console.log('Response:');
      console.log(data);
      process.exit(1);
    }
  });
});

req.on('error', (error) => {
  log('red', `✗ Error: Cannot reach API at ${API_HOST}`);
  console.log('Make sure the backend is running:');
  console.log('  cd backend && uvicorn main:app --reload');
  console.log(`\nError details: ${error.message}`);
  process.exit(1);
});

req.setTimeout(10000, () => {
  log('red', '✗ Error: Request timeout');
  req.destroy();
  process.exit(1);
});
