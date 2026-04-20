const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const backendDir = path.join(__dirname, '..', 'backend');
const venvDir = path.join(backendDir, 'venv');
const isWindows = process.platform === 'win32';

const pythonExe = isWindows
  ? path.join(venvDir, 'Scripts', 'python.exe')
  : path.join(venvDir, 'bin', 'python');

const pipExe = isWindows
  ? path.join(venvDir, 'Scripts', 'pip.exe')
  : path.join(venvDir, 'bin', 'pip');

console.log('🔧 Setting up Python backend...\n');

// Create venv if it doesn't exist
if (!fs.existsSync(venvDir)) {
  console.log('📦 Creating virtual environment...');
  try {
    execSync('python -m venv venv', { cwd: backendDir, stdio: 'inherit' });
    console.log('✅ Virtual environment created\n');
  } catch (error) {
    console.error('❌ Failed to create virtual environment');
    process.exit(1);
  }
} else {
  console.log('✅ Virtual environment already exists\n');
}

// Install dependencies
console.log('📦 Installing Python dependencies...');
try {
  execSync(`"${pipExe}" install -r requirements.txt`, {
    cwd: backendDir,
    stdio: 'inherit'
  });
  console.log('\n✅ Backend dependencies installed successfully!');
} catch (error) {
  console.error('❌ Failed to install dependencies');
  process.exit(1);
}
