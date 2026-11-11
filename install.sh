#!/usr/bin/env bash
# PirateGit Installation Script for macOS & Linux
set -euo pipefail

echo -e "\033[1;36m🏴‍☠️ Installing PirateGit Agent Skills...\033[0m"

ANTIGRAVITY_SKILLS="$HOME/.gemini/config/skills"
CLAUDE_SKILLS="$HOME/.claude/skills"
SOURCE_DIR=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/skills/explore" ]; then
    SOURCE_DIR="$SCRIPT_DIR"
else
    TEMP_DIR=$(mktemp -d)
    echo -e "\033[1;33m📥 Downloading latest PirateGit release from GitHub...\033[0m"
    curl -fsSL "https://github.com/username/PirateGit/archive/refs/heads/main.tar.gz" | tar -xz -C "$TEMP_DIR"
    SOURCE_DIR="$TEMP_DIR/PirateGit-main"
fi

# 1. Antigravity installation
if [ -d "$HOME/.gemini" ]; then
    mkdir -p "$ANTIGRAVITY_SKILLS/explore"
    mkdir -p "$ANTIGRAVITY_SKILLS/loot"
    mkdir -p "$ANTIGRAVITY_SKILLS/github-repo-scout/scripts"

    cp "$SOURCE_DIR/skills/explore/SKILL.md" "$ANTIGRAVITY_SKILLS/explore/SKILL.md"
    cp "$SOURCE_DIR/skills/loot/SKILL.md" "$ANTIGRAVITY_SKILLS/loot/SKILL.md"
    cp "$SOURCE_DIR/scripts/pirategit.py" "$ANTIGRAVITY_SKILLS/github-repo-scout/scripts/github_scout.py"
    chmod +x "$ANTIGRAVITY_SKILLS/github-repo-scout/scripts/github_scout.py"
    echo -e "\033[1;32m✅ Installed into Google Antigravity ($ANTIGRAVITY_SKILLS)\033[0m"
fi

# 2. Claude Code installation
if [ -d "$HOME/.claude" ]; then
    mkdir -p "$CLAUDE_SKILLS/explore"
    mkdir -p "$CLAUDE_SKILLS/loot"
    cp "$SOURCE_DIR/skills/explore/SKILL.md" "$CLAUDE_SKILLS/explore/SKILL.md"
    cp "$SOURCE_DIR/skills/loot/SKILL.md" "$CLAUDE_SKILLS/loot/SKILL.md"
    echo -e "\033[1;32m✅ Installed into Claude Code ($CLAUDE_SKILLS)\033[0m"
fi

echo -e "\033[1;36m🎉 PirateGit is ready! Use /explore and /loot in your agent chat.\033[0m"

