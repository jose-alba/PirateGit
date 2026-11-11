# PirateGit Installation Script for Windows (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "🏴‍☠️ Installing PirateGit Agent Skills..." -ForegroundColor Cyan

$AntigravitySkills = "$env:USERPROFILE\.gemini\config\skills"
$ClaudeSkills = "$env:USERPROFILE\.claude\skills"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Determine source directories
if (Test-Path "$ScriptDir\skills\explore") {
    $SourceRoot = $ScriptDir
} else {
    $TempZip = "$env:TEMP\PirateGit-main.zip"
    $TempExtract = "$env:TEMP\PirateGit-main"
    Write-Host "📥 Downloading latest PirateGit release from GitHub..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://github.com/username/PirateGit/archive/refs/heads/main.zip" -OutFile $TempZip
    Expand-Archive -Path $TempZip -DestinationPath $env:TEMP -Force
    $SourceRoot = "$env:TEMP\PirateGit-main"
}

# 2. Install to Antigravity
if (Test-Path "$env:USERPROFILE\.gemini") {
    New-Item -ItemType Directory -Force -Path "$AntigravitySkills\explore" | Out-Null
    New-Item -ItemType Directory -Force -Path "$AntigravitySkills\loot" | Out-Null
    New-Item -ItemType Directory -Force -Path "$AntigravitySkills\github-repo-scout\scripts" | Out-Null

    Copy-Item "$SourceRoot\skills\explore\SKILL.md" "$AntigravitySkills\explore\SKILL.md" -Force
    Copy-Item "$SourceRoot\skills\loot\SKILL.md" "$AntigravitySkills\loot\SKILL.md" -Force
    Copy-Item "$SourceRoot\scripts\pirategit.py" "$AntigravitySkills\github-repo-scout\scripts\github_scout.py" -Force
    Write-Host "✅ Installed into Google Antigravity ($AntigravitySkills)" -ForegroundColor Green
}

# 3. Install to Claude Code (if present)
if (Test-Path "$env:USERPROFILE\.claude") {
    New-Item -ItemType Directory -Force -Path "$ClaudeSkills\explore" | Out-Null
    New-Item -ItemType Directory -Force -Path "$ClaudeSkills\loot" | Out-Null
    Copy-Item "$SourceRoot\skills\explore\SKILL.md" "$ClaudeSkills\explore\SKILL.md" -Force
    Copy-Item "$SourceRoot\skills\loot\SKILL.md" "$ClaudeSkills\loot\SKILL.md" -Force
    Write-Host "✅ Installed into Claude Code ($ClaudeSkills)" -ForegroundColor Green
}

Write-Host "🎉 PirateGit is ready! Use /explore and /loot in your agent chat." -ForegroundColor Cyan

