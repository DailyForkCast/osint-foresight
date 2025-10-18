#!/usr/bin/env python3
"""
setup_git_hooks.py - Git Hooks Configuration

Sets up git hooks for documentation validation:
- Pre-commit: Validates documentation before commits
- Pre-push: Runs comprehensive validation before push

Usage:
    python setup_git_hooks.py               # Install all hooks
    python setup_git_hooks.py --remove      # Remove hooks
    python setup_git_hooks.py --test        # Test hooks without installing
"""

import os
import sys
import stat
from pathlib import Path
import argparse

PROJECT_ROOT = Path("C:/Projects/OSINT - Foresight")
GIT_HOOKS_DIR = PROJECT_ROOT / ".git" / "hooks"

# Pre-commit hook content
PRE_COMMIT_HOOK = '''#!/bin/bash
# Pre-commit hook for OSINT Foresight documentation validation
# Automatically installed by setup_git_hooks.py

echo "Running documentation validation..."

# Run validation script
python "C:/Projects/OSINT - Foresight/validate_documentation.py" --hook

# Capture exit code
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "[ERROR] COMMIT BLOCKED: Documentation validation failed"
    echo "   Fix errors above before committing"
    echo ""
    echo "To bypass this check (not recommended):"
    echo "   git commit --no-verify"
    echo ""
    exit 1
fi

echo "[OK] Documentation validation passed"
exit 0
'''

# Pre-push hook content
PRE_PUSH_HOOK = '''#!/bin/bash
# Pre-push hook for OSINT Foresight comprehensive validation
# Automatically installed by setup_git_hooks.py

echo "Running comprehensive validation before push..."

# Run full validation
python "C:/Projects/OSINT - Foresight/validate_documentation.py"

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "[WARNING]  WARNING: Documentation issues detected"
    echo "   Consider fixing before pushing"
    echo ""
    read -p "Push anyway? (yes/no): " response
    if [ "$response" != "yes" ]; then
        echo "Push cancelled"
        exit 1
    fi
fi

echo "[OK] Proceeding with push"
exit 0
'''


def make_executable(file_path: Path):
    """Make a file executable on Unix-like systems"""
    if os.name != 'nt':  # Not Windows
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC)


def install_hook(hook_name: str, hook_content: str) -> bool:
    """Install a git hook"""
    hook_path = GIT_HOOKS_DIR / hook_name

    try:
        # Backup existing hook if present
        if hook_path.exists():
            backup_path = hook_path.with_suffix('.backup')
            print(f"  [BACKUP] Backing up existing {hook_name} to {backup_path.name}")
            hook_path.rename(backup_path)

        # Write new hook
        with open(hook_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(hook_content)

        # Make executable
        make_executable(hook_path)

        print(f"  [OK] Installed {hook_name}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to install {hook_name}: {e}")
        return False


def remove_hook(hook_name: str) -> bool:
    """Remove a git hook"""
    hook_path = GIT_HOOKS_DIR / hook_name

    try:
        if hook_path.exists():
            # Check if there's a backup to restore
            backup_path = hook_path.with_suffix('.backup')
            if backup_path.exists():
                print(f"  [RESTORE] Restoring backup for {hook_name}")
                backup_path.rename(hook_path)
            else:
                hook_path.unlink()
                print(f"  [OK] Removed {hook_name}")
        else:
            print(f"  [INFO]  {hook_name} not found")

        return True

    except Exception as e:
        print(f"  [ERROR] Failed to remove {hook_name}: {e}")
        return False


def test_hooks():
    """Test hook scripts without installing"""
    print(f"\n{'='*60}")
    print("Testing Hook Scripts")
    print(f"{'='*60}\n")

    print("Pre-commit hook content:")
    print(PRE_COMMIT_HOOK)
    print("\n" + "="*60)

    print("\nPre-push hook content:")
    print(PRE_PUSH_HOOK)
    print("\n" + "="*60)

    print("\n[OK] Hook scripts validated")
    print("   Use without --test to install")


def main():
    parser = argparse.ArgumentParser(
        description="Setup git hooks for OSINT Foresight documentation validation"
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove installed hooks"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test hooks without installing"
    )

    args = parser.parse_args()

    print(f"\n{'#'*60}")
    print("# OSINT Foresight - Git Hooks Setup")
    print(f"{'#'*60}\n")

    # Test mode
    if args.test:
        test_hooks()
        return 0

    # Check if .git directory exists
    if not GIT_HOOKS_DIR.exists():
        print(f"[ERROR] Error: Git hooks directory not found: {GIT_HOOKS_DIR}")
        print("   Are you in a git repository?")
        return 1

    # Remove mode
    if args.remove:
        print("Removing git hooks...\n")
        remove_hook("pre-commit")
        remove_hook("pre-push")
        print("\n[OK] Git hooks removed")
        return 0

    # Install mode
    print("Installing git hooks...\n")

    success = True
    success &= install_hook("pre-commit", PRE_COMMIT_HOOK)
    success &= install_hook("pre-push", PRE_PUSH_HOOK)

    if success:
        print(f"\n{'='*60}")
        print("[OK] Git hooks successfully installed!")
        print(f"{'='*60}")
        print("\nInstalled hooks:")
        print("  - pre-commit: Validates documentation before commit")
        print("  - pre-push: Comprehensive validation before push")
        print("\nTo bypass hooks (not recommended):")
        print("  git commit --no-verify")
        print("  git push --no-verify")
        print(f"\n{'='*60}\n")
    else:
        print("\n[ERROR] Some hooks failed to install")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
