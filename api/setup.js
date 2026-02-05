const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// 가상 환경 경로
const venvPath = path.join(__dirname, '.venv');
const venvScriptsPath = path.join(venvPath, 'Scripts');
const venvActivatePath = path.join(venvScriptsPath, 'activate');

// 필요한 패키지 목록
const requiredPackages = [
  'fastapi',
  'uvicorn',
  'python-multipart',
  'numpy',
  'pillow'
];

// 가상 환경 생성 함수
function createVirtualEnv() {
  return new Promise((resolve, reject) => {
    console.log('Creating virtual environment...');
    
    // 가상 환경이 이미 존재하는지 확인
    if (fs.existsSync(venvPath)) {
      console.log('Virtual environment already exists.');
      return resolve();
    }
    
    // 가상 환경 생성
    const venvProcess = spawn('python', ['-m', 'venv', '.venv'], {
      cwd: __dirname,
      stdio: 'inherit',
      shell: true
    });
    
    venvProcess.on('close', (code) => {
      if (code === 0) {
        console.log('Virtual environment created successfully.');
        resolve();
      } else {
        reject(new Error(`Failed to create virtual environment. Exit code: ${code}`));
      }
    });
    
    venvProcess.on('error', (err) => {
      reject(new Error(`Failed to create virtual environment: ${err.message}`));
    });
  });
}

// 패키지 설치 함수
function installPackages() {
  return new Promise((resolve, reject) => {
    console.log('Installing required packages...');
    
    // Windows에서는 PowerShell을 사용하여 가상 환경 활성화 후 패키지 설치
    const command = process.platform === 'win32'
      ? `powershell -Command ".\\venv\\Scripts\\Activate.ps1; pip install ${requiredPackages.join(' ')}"`
      : `source .venv/bin/activate && pip install ${requiredPackages.join(' ')}`;
    
    const installProcess = spawn(process.platform === 'win32' ? 'cmd' : 'bash', [
      process.platform === 'win32' ? '/c' : '-c',
      command
    ], {
      cwd: __dirname,
      stdio: 'inherit',
      shell: true
    });
    
    installProcess.on('close', (code) => {
      if (code === 0) {
        console.log('Packages installed successfully.');
        resolve();
      } else {
        reject(new Error(`Failed to install packages. Exit code: ${code}`));
      }
    });
    
    installProcess.on('error', (err) => {
      reject(new Error(`Failed to install packages: ${err.message}`));
    });
  });
}

// 메인 함수
async function main() {
  try {
    await createVirtualEnv();
    await installPackages();
    console.log('Setup completed successfully.');
  } catch (error) {
    console.error('Setup failed:', error.message);
    process.exit(1);
  }
}

// 스크립트 실행
main(); 