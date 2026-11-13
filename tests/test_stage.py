#!/usr/bin/env python3
"""
Unit tests for PirateGit stage.py minitool.
"""

import shutil
import sys
from pathlib import Path

# Add skills to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills"))

from loot.scripts.stage import STAGING_DIR, cmd_add, cmd_complete, cmd_status, load_manifest


def test_stage_lifecycle():
    # Setup dummy files
    dummy_src = Path("tests/dummy_loot_source.py")
    dummy_src.write_text("def borrowed_func():\n    return 42\n", encoding="utf-8")

    dummy_dest = Path("tests/dummy_target.py")
    dummy_dest.write_text("def my_app():\n    pass\n", encoding="utf-8")

    try:
        # 1. Test add
        cmd_add(str(dummy_src), repo="dummy/repo", license_name="MIT")
        manifest = load_manifest()
        assert len(manifest) == 1
        staged_key = list(manifest.keys())[0]
        assert Path(staged_key).exists()

        # 2. Test complete
        cmd_complete(staged_key, dest_file=str(dummy_dest), repo="dummy/repo", license_name="MIT")

        # Verify staged file was burned down (deleted)
        assert not Path(staged_key).exists()

        # Verify provenance was injected into target
        dest_content = dummy_dest.read_text(encoding="utf-8")
        assert "[PIRATEGIT LOOT PROVENANCE]" in dest_content
        assert "https://github.com/dummy/repo" in dest_content

        print("✅ Staging lifecycle test passed!")
    finally:
        # Cleanup
        if dummy_src.exists():
            dummy_src.unlink()
        if dummy_dest.exists():
            dummy_dest.unlink()
        if STAGING_DIR.exists():
            shutil.rmtree(STAGING_DIR, ignore_errors=True)


if __name__ == "__main__":
    test_stage_lifecycle()
