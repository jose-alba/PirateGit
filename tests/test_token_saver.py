#!/usr/bin/env python3
"""
Unit tests for PirateGit smart token saver output truncation.
"""

import sys
from pathlib import Path

# Add skills to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills"))

from common.utils import smart_truncate_output


def test_smart_truncate_short_text():
    text = "line 1\nline 2\nline 3"
    result = smart_truncate_output(text, max_lines=10, max_chars=100)
    assert result == text


def test_smart_truncate_collapses_middle_lines():
    lines = [f"line {i}" for i in range(50)]
    text = "\n".join(lines)
    result = smart_truncate_output(text, max_lines=10, max_chars=5000, keep_head=3, keep_tail=2)
    assert "line 0" in result
    assert "line 1" in result
    assert "line 2" in result
    assert "line 48" in result
    assert "line 49" in result
    assert "45 lines collapsed" in result


if __name__ == "__main__":
    test_smart_truncate_short_text()
    test_smart_truncate_collapses_middle_lines()
    print("✅ All token saver tests passed!")
