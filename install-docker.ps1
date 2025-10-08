# Docker Desktop Installation Script
# Simple version for downloading and installing Docker Desktop

Write-Host "============================================================"
Write-Host "Docker Desktop Installation"
Write-Host "============================================================"

# Check if Docker is already installed
Write-Host "`nChecking Docker installation..."

try {
    $version = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker is already installed: $version" -ForegroundColor Green
        Write-Host "`nYou can run: .\start-mysql.ps1" -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "Docker is not installed." -ForegroundColor Yellow
}

# Try winget first
Write-Host "`nTrying to install via winget..."
try {
    winget --version 2>$null | Out-Null
    Write-Host "Using winget to install Docker Desktop..." -ForegroundColor Green

    winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nDocker Desktop installed successfully!" -ForegroundColor Green
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "1. Restart your computer"
        Write-Host "2. Start Docker Desktop"
        Write-Host "3. Wait for Docker to start (1-2 minutes)"
        Write-Host "4. Run: .\start-mysql.ps1"
        exit 0
    }
} catch {
    Write-Host "winget not available, trying manual download..." -ForegroundColor Yellow
}

# Manual download
Write-Host "`nDownloading Docker Desktop installer..."
$url = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$output = "$env:TEMP\DockerDesktopInstaller.exe"

Write-Host "Download URL: $url"
Write-Host "Save to: $output"

try {
    Write-Host "`nDownloading (about 500 MB)..." -ForegroundColor Yellow

    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $url -OutFile $output

    Write-Host "Download completed!" -ForegroundColor Green

    Write-Host "`nStarting installation..." -ForegroundColor Yellow
    Start-Process -FilePath $output -Wait

    Write-Host "`nInstallation completed!" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Restart your computer (required)"
    Write-Host "2. Start Docker Desktop"
    Write-Host "3. Accept terms"
    Write-Host "4. Wait for Docker to start"
    Write-Host "5. Run: docker --version"
    Write-Host "6. Run: .\start-mysql.ps1"

} catch {
    Write-Host "`nDownload failed: $_" -ForegroundColor Red
    Write-Host "`nPlease download manually from:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop"

    Start-Process "https://www.docker.com/products/docker-desktop"
}

Write-Host "`nFor detailed instructions, see: DOCKER_INSTALL.md"
