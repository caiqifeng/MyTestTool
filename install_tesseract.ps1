<#
.SYNOPSIS
    One-click Tesseract OCR installer with Chinese language packs
.DESCRIPTION
    Installs Tesseract OCR 5.4.0 silently, downloads chi_sim + chi_tra language data,
    and configures TESSDATA_PREFIX + PATH environment variables.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install_tesseract.ps1
#>
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$TesseractUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
$InstallerPath = "$env:TEMP\tesseract-installer.exe"
$InstallDir = "C:\Program Files\Tesseract-OCR"

$LangData = @{
    "chi_sim" = "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata"
    "chi_tra" = "https://github.com/tesseract-ocr/tessdata/raw/main/chi_tra.traineddata"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tesseract OCR One-Click Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---- Step 1: Install Tesseract ----
if (Test-Path "$InstallDir\tesseract.exe") {
    Write-Host "[1/3] Tesseract already installed: $InstallDir" -ForegroundColor Green
} else {
    Write-Host "[1/3] Downloading Tesseract installer..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $TesseractUrl -OutFile $InstallerPath -UseBasicParsing
    } catch {
        Write-Host "ERROR: Download failed: $_" -ForegroundColor Red
        Write-Host "Please download manually from: $TesseractUrl" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "[1/3] Installing Tesseract (silent mode)..." -ForegroundColor Yellow
    Start-Process -FilePath $InstallerPath -ArgumentList "/SILENT" -Wait -NoNewWindow
    Remove-Item $InstallerPath -Force

    if (Test-Path "$InstallDir\tesseract.exe") {
        Write-Host "[1/3] Install OK" -ForegroundColor Green
    } else {
        Write-Host "[1/3] Install FAILED. Download manually from:" -ForegroundColor Red
        Write-Host "       $TesseractUrl" -ForegroundColor Yellow
        exit 1
    }
}

# ---- Step 2: Download Chinese language packs ----
Write-Host "[2/3] Downloading Chinese language packs..." -ForegroundColor Yellow

$UserTessdata = "$env:USERPROFILE\tessdata"
if (-not (Test-Path $UserTessdata)) {
    New-Item -ItemType Directory -Path $UserTessdata -Force | Out-Null
}

foreach ($lang in $LangData.Keys) {
    $dest = "$UserTessdata\$lang.traineddata"
    if (Test-Path $dest) {
        Write-Host "       $lang already exists, skip" -ForegroundColor Green
    } else {
        Write-Host "       Downloading $lang ..." -ForegroundColor Gray
        try {
            Invoke-WebRequest -Uri $LangData[$lang] -OutFile $dest -UseBasicParsing
            $sizeMB = [math]::Round((Get-Item $dest).Length / 1MB, 1)
            Write-Host "       $lang OK ($sizeMB MB)" -ForegroundColor Green
        } catch {
            Write-Host "       $lang FAILED: $_" -ForegroundColor Red
        }
    }
}

# ---- Step 3: Set environment variables ----
Write-Host "[3/3] Configuring environment variables..." -ForegroundColor Yellow

$currentPrefix = [Environment]::GetEnvironmentVariable("TESSDATA_PREFIX", "User")
if ($currentPrefix -ne $env:USERPROFILE) {
    [Environment]::SetEnvironmentVariable("TESSDATA_PREFIX", $env:USERPROFILE, "User")
    Write-Host "       Set TESSDATA_PREFIX=$env:USERPROFILE" -ForegroundColor Green
} else {
    Write-Host "       TESSDATA_PREFIX already set, skip" -ForegroundColor Green
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*Tesseract-OCR*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$InstallDir", "User")
    Write-Host "       Added Tesseract to PATH" -ForegroundColor Green
} else {
    Write-Host "       PATH already includes Tesseract, skip" -ForegroundColor Green
}

# ---- Verify ----
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Verification:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
$env:Path = "$InstallDir;$env:Path"
$env:TESSDATA_PREFIX = $env:USERPROFILE
& "$InstallDir\tesseract.exe" --list-langs 2>&1 | ForEach-Object {
    if ($_ -match "chi_sim|chi_tra|eng") {
        Write-Host "  [OK] $_" -ForegroundColor Green
    }
}
Write-Host ""
Write-Host "Usage: -l chi_sim+chi_tra+eng" -ForegroundColor Gray
Write-Host "Note: Restart terminal for env vars to take effect" -ForegroundColor Yellow
