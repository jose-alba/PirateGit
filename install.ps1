# PirateGit Installation Script for Windows (PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "🏴‍☠️ Installing PirateGit Agent Skills..." -ForegroundColor Cyan

$AntigravitySkills = "$env:USERPROFILE\.gemini\config\skills"
$ClaudeSkills = "$env:USERPROFILE\.claude\skills"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Determine source directories
if (Test-Path "$ScriptDir\skills\explore") {
    $SourceRoot = "$ScriptDir\skills"
} else {
    $TempZip = "$env:TEMP\PirateGit-main.zip"
    Write-Host "📥 Downloading latest PirateGit release from GitHub..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://github.com/username/PirateGit/archive/refs/heads/main.zip" -OutFile $TempZip
    Expand-Archive -Path $TempZip -DestinationPath $env:TEMP -Force
    $SourceRoot = "$env:TEMP\PirateGit-main\skills"
}

# 2. Install to Antigravity
if (Test-Path "$env:USERPROFILE\.gemini") {
    New-Item -ItemType Directory -Force -Path "$AntigravitySkills\explore" | Out-Null
    New-Item -ItemType Directory -Force -Path "$AntigravitySkills\loot" | Out-Null

    Copy-Item "$SourceRoot\explore\*" "$AntigravitySkills\explore\" -Recurse -Force
    Copy-Item "$SourceRoot\loot\*" "$AntigravitySkills\loot\" -Recurse -Force

    # Distribute shared common package into each skill so they are 100% self-contained
    New-Item -ItemType Directory -Force -Path "$AntigravitySkills\explore\scripts\common" | Out-Null
    New-Item -ItemType Directory -Force -Path "$AntigravitySkills\loot\scripts\common" | Out-Null
    Copy-Item "$SourceRoot\common\*" "$AntigravitySkills\explore\scripts\common\" -Recurse -Force
    Copy-Item "$SourceRoot\common\*" "$AntigravitySkills\loot\scripts\common\" -Recurse -Force
    Write-Host "✅ Installed into Google Antigravity ($AntigravitySkills)" -ForegroundColor Green
}

# 3. Install to Claude Code (if present)
if (Test-Path "$env:USERPROFILE\.claude") {
    New-Item -ItemType Directory -Force -Path "$ClaudeSkills\explore" | Out-Null
    New-Item -ItemType Directory -Force -Path "$ClaudeSkills\loot" | Out-Null

    Copy-Item "$SourceRoot\explore\*" "$ClaudeSkills\explore\" -Recurse -Force
    Copy-Item "$SourceRoot\loot\*" "$ClaudeSkills\loot\" -Recurse -Force

    # Distribute shared common package into each skill so they are 100% self-contained
    New-Item -ItemType Directory -Force -Path "$ClaudeSkills\explore\scripts\common" | Out-Null
    New-Item -ItemType Directory -Force -Path "$ClaudeSkills\loot\scripts\common" | Out-Null
    Copy-Item "$SourceRoot\common\*" "$ClaudeSkills\explore\scripts\common\" -Recurse -Force
    Copy-Item "$SourceRoot\common\*" "$ClaudeSkills\loot\scripts\common\" -Recurse -Force
    Write-Host "✅ Installed into Claude Code ($ClaudeSkills)" -ForegroundColor Green
}

Write-Host "🎉 PirateGit is ready! Use /explore and /loot in your agent chat." -ForegroundColor Cyan
