#!/usr/bin/env python3
"""
Update dependencies to latest stable versions with compatibility checks
"""
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def backup_requirements():
    """Backup current requirements.txt"""
    requirements = Path("requirements.txt")
    if requirements.exists():
        backup = Path(f"requirements.txt.backup.{int(time.time())}")
        requirements.rename(backup)
        print(f"✅ Backed up requirements.txt to {backup}")
        return backup
    return None


def update_dependencies() -> bool:
    """Update dependencies step-by-step"""
    print("=== TwisterLab Dependency Update ===\n")

    # 1. Backup
    backup = backup_requirements()

    # 2. Install pip-review
    print("Installing pip-review...")
    run_command([sys.executable, "-m", "pip", "install", "pip-review"])

    # 3. Show outdated packages
    print("\n📋 Outdated packages:")
    code, stdout, _ = run_command([sys.executable, "-m", "pip", "list", "--outdated"])
    print(stdout)

    # 4. Critical updates first (security)
    critical = ["fastapi", "pydantic", "starlette", "uvicorn", "httpx"]

    print("\n⚠️  Updating critical packages...")
    for pkg in critical:
        print(f"  Updating {pkg}...")
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", pkg])

    # 5. Pydantic V2 migration (special handling)
    print("\n🔄 Migrating to Pydantic V2...")
    run_command([sys.executable, "-m", "pip", "install", "pydantic>=2.0"])

    print("\n⚠️  Pydantic V2 Breaking Changes - Manual Review Required:")
    print("  - BaseModel.dict() → model_dump()")
    print("  - BaseModel.parse_obj() → model_validate()")
    print("  - @validator → @field_validator")
    print("  - Config class → model_config dict")
    print("\n  Run: bump-pydantic src/")

    # 6. Update all other packages
    print("\n📦 Updating remaining packages...")
    run_command([sys.executable, "-m", "pip-review", "--auto"])

    # 7. Freeze new requirements
    print("\n💾 Freezing requirements...")
    code, stdout, _ = run_command([sys.executable, "-m", "pip", "freeze"])
    Path("requirements.txt").write_text(stdout)

    # 8. Run tests
    print("\n🧪 Running tests to verify compatibility...")
    test_code, test_out, test_err = run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v"]
    )

    if test_code != 0:
        print("\n❌ Tests failed after update!")
        print("Stderr:", test_err)
        if backup:
            print(f"\n⚠️  Consider rolling back: mv {backup} requirements.txt")
        return False

    print("\n✅ All tests passed! Dependencies updated successfully.")
    return True


if __name__ == "__main__":
    success = update_dependencies()
    sys.exit(0 if success else 1)
