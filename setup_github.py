#!/usr/bin/env python3
"""
TwisterLab GitHub Repository Setup Script
Run this script to push the local repository to GitHub
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def main():
    print("🚀 TwisterLab GitHub Repository Setup")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists("README.md") or not os.path.exists("core/twisterlang_encoder.py"):
        print("❌ Error: Please run this script from the twisterlab-repo directory")
        sys.exit(1)

    print("📋 Prerequisites check:")
    print("1. Create a new repository on GitHub: https://github.com/new")
    print("   - Repository name: twisterlab")
    print("   - Owner: youneselfakir0")
    print("   - Make it public")
    print("   - Do NOT initialize with README, .gitignore, or license")
    print("2. Copy the repository URL (HTTPS): https://github.com/youneselfakir0/twisterlab.git")

    repo_url = input("\n🔗 Enter your GitHub repository URL: ").strip()

    if not repo_url or "github.com" not in repo_url:
        print("❌ Invalid GitHub URL. Please try again.")
        sys.exit(1)

    # Set remote origin
    if not run_command(f'git remote add origin "{repo_url}"', "Setting remote origin"):
        sys.exit(1)

    # Push to GitHub
    if not run_command("git push -u origin master", "Pushing to GitHub"):
        print("\n💡 If push fails, you may need to:")
        print("   1. Set up SSH keys or personal access token")
        print("   2. Configure git credentials:")
        print('      git config --global user.name "Your Name"')
        print('      git config --global user.email "your.email@example.com"')
        sys.exit(1)

    # Verify the push
    if not run_command("git remote -v", "Verifying remote configuration"):
        sys.exit(1)

    print("\n🎉 SUCCESS! TwisterLab repository is now live on GitHub!")
    print("\n📋 Next steps:")
    print("1. Visit: https://github.com/youneselfakir0/twisterlab")
    print("2. Enable GitHub Actions (should auto-enable)")
    print("3. Check that CI/CD tests are running")
    print("4. Ready for Phase 1 development!")

    print("\n🔗 Repository links:")
    print(f"• GitHub: https://github.com/youneselfakir0/twisterlab")
    print(f"• Actions: https://github.com/youneselfakir0/twisterlab/actions")
    print(f"• Issues: https://github.com/youneselfakir0/twisterlab/issues")


if __name__ == "__main__":
    main()
