# cleanup_for_github.ps1
# PowerShell script to clean up project before GitHub upload

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Cleaning Project for GitHub Upload" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Remove Python cache
Write-Host "[1/6] Removing Python cache files..." -ForegroundColor Yellow
if (Test-Path "__pycache__") {
    Remove-Item -Recurse -Force "__pycache__"
    Write-Host "  ✓ Removed __pycache__" -ForegroundColor Green
}
if (Test-Path "core/__pycache__") {
    Remove-Item -Recurse -Force "core/__pycache__"
    Write-Host "  ✓ Removed core/__pycache__" -ForegroundColor Green
}

# Remove alert images
Write-Host "[2/6] Clearing alert images..." -ForegroundColor Yellow
$alertFiles = Get-ChildItem "output/alerts" -Include *.jpg,*.png -File
if ($alertFiles.Count -gt 0) {
    $alertFiles | Remove-Item -Force
    Write-Host "  ✓ Removed $($alertFiles.Count) alert image(s)" -ForegroundColor Green
} else {
    Write-Host "  ✓ No alert images to remove" -ForegroundColor Green
}

# Remove log files
Write-Host "[3/6] Removing log files..." -ForegroundColor Yellow
$logFiles = Get-ChildItem -Filter "*.log" -File
if ($logFiles.Count -gt 0) {
    $logFiles | Remove-Item -Force
    Write-Host "  ✓ Removed $($logFiles.Count) log file(s)" -ForegroundColor Green
} else {
    Write-Host "  ✓ No log files to remove" -ForegroundColor Green
}

# Check for large files
Write-Host "[4/6] Checking for large files (>50MB)..." -ForegroundColor Yellow
$largeFiles = Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt 50MB }
if ($largeFiles.Count -gt 0) {
    Write-Host "  ⚠ Warning: Found large files:" -ForegroundColor Red
    foreach ($file in $largeFiles) {
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        Write-Host "    - $($file.Name): ${sizeMB}MB" -ForegroundColor Red
    }
    Write-Host "  Consider excluding these from GitHub!" -ForegroundColor Red
} else {
    Write-Host "  ✓ No large files found" -ForegroundColor Green
}

# Check for video files
Write-Host "[5/6] Checking for video files..." -ForegroundColor Yellow
$videoFiles = Get-ChildItem -Recurse -Include *.mp4,*.avi,*.mov,*.mkv -File
if ($videoFiles.Count -gt 0) {
    Write-Host "  ⚠ Warning: Found video files:" -ForegroundColor Red
    foreach ($file in $videoFiles) {
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        Write-Host "    - $($file.Name): ${sizeMB}MB" -ForegroundColor Red
    }
    Write-Host "  These are already in .gitignore" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ No video files found" -ForegroundColor Green
}

# Summary
Write-Host "[6/6] Generating summary..." -ForegroundColor Yellow
$totalFiles = (Get-ChildItem -Recurse -File | Measure-Object).Count
$totalSize = [math]::Round((Get-ChildItem -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Cleanup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project Statistics:" -ForegroundColor Cyan
Write-Host "  Total Files: $totalFiles" -ForegroundColor White
Write-Host "  Total Size: ${totalSize}MB" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review GITHUB_UPLOAD_GUIDE.md" -ForegroundColor White
Write-Host "  2. Update personal info in README.md and LICENSE" -ForegroundColor White
Write-Host "  3. Test the program: python main.py" -ForegroundColor White
Write-Host "  4. Initialize git: git init" -ForegroundColor White
Write-Host "  5. Upload to GitHub!" -ForegroundColor White
Write-Host ""
