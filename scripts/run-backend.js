const { spawn } = require('child_process');
const path = require('path');

const backendDir = path.join(__dirname, '..', 'backend');
const isWindows = process.platform === 'win32';

const pythonExe = isWindows
  ? path.join(backendDir, 'venv', 'Scripts', 'python.exe')
  : path.join(backendDir, 'venv', 'bin', 'python');

console.log('🚀 Starting backend server...\n');

const backend = spawn(
  pythonExe,
  ['-m', 'uvicorn', 'main:app', '--reload', '--port', '8000'],
  {
    cwd: backendDir,
    stdio: 'inherit',
    shell: true
  }
);

backend.on('error', (error) => {
  console.error('❌ Failed to start backend:', error.message);
  process.exit(1);
});

backend.on('close', (code) => {
  if (code !== 0) {
    console.error(`❌ Backend exited with code ${code}`);
  }
  process.exit(code);
});

// Handle Ctrl+C
process.on('SIGINT', () => {
  backend.kill('SIGINT');
});
