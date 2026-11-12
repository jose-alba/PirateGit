#!/usr/bin/env bash
# PirateGit Installation Script for macOS & Linux
set -euo pipefail

echo -e "\033[1;36m🏴‍☠️ Installing PirateGit Agent Skills...\033[0m"

ANTIGRAVITY_SKILLS="$HOME/.gemini/config/skills"
CLAUDE_SKILLS="$HOME/.claude/skills"
SOURCE_ROOT=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/skills/explore" ]; then
    SOURCE_ROOT="$SCRIPT_DIR/skills"
else
    TEMP_DIR=$(mktemp -d)
    echo -e "\033[1;33m📥 Downloading latest PirateGit release from GitHub...\033[0m"
    curl -fsSL "https://github.com/username/PirateGit/archive/refs/heads/main.tar.gz" | tar -xz -C "$TEMP_DIR"
    SOURCE_ROOT="$TEMP_DIR/PirateGit-main/skills"
fi

# 1. Antigravity installation
if [ -d "$HOME/.gemini" ]; then
    mkdir -p "$ANTIGRAVITY_SKILLS/explore"
    mkdir -p "$ANTIGRAVITY_SKILLS/loot"

    cp -R "$SOURCE_ROOT/explore/"* "$ANTIGRAVITY_SKILLS/explore/"
    cp -R "$SOURCE_ROOT/loot/"* "$ANTIGRAVITY_SKILLS/loot/"

    # Distribute shared common package into each skill so they are 100% self-contained
    mkdir -p "$ANTIGRAVITY_SKILLS/explore/scripts/common"
    mkdir -p "$ANTIGRAVITY_SKILLS/loot/scripts/common"
    cp -R "$SOURCE_ROOT/common/"* "$ANTIGRAVITY_SKILLS/explore/scripts/common/"
    cp -R "$SOURCE_ROOT/common/"* "$ANTIGRAVITY_SKILLS/loot/scripts/common/"
    echo -e "\033[1;32m✅ Installed into Google Antigravity ($ANTIGRAVITY_SKILLS)\033[0m"
fi

# 2. Claude Code installation
if [ -d "$HOME/.claude" ]; then
    mkdir -p "$CLAUDE_SKILLS/explore"
    mkdir -p "$CLAUDE_SKILLS/loot"

    cp -R "$SOURCE_ROOT/explore/"* "$CLAUDE_SKILLS/explore/"
    cp -R "$SOURCE_ROOT/loot/"* "$CLAUDE_SKILLS/loot/"

    # Distribute shared common package into each skill so they are 100% self-contained
    mkdir -p "$CLAUDE_SKILLS/explore/scripts/common"
    mkdir -p "$CLAUDE_SKILLS/loot/scripts/common"
    cp -R "$SOURCE_ROOT/common/"* "$CLAUDE_SKILLS/explore/scripts/common/"
    cp -R "$SOURCE_ROOT/common/"* "$CLAUDE_SKILLS/loot/scripts/common/"
    echo -e "\033[1;32m✅ Installed into Claude Code ($CLAUDE_SKILLS)\033[0m"
fi

echo -e "\033[1;36m🎉 PirateGit is ready! Use /explore and /loot in your agent chat.\033[0m"
