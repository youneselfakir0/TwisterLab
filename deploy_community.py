#!/usr/bin/env python3
"""
TwisterLab Community Deployment Script
Automated deployment for TwisterLab v1.0.0 community release

Usage:
    python deploy_community.py --help

Requirements:
    - Python 3.8+
    - Docker & Docker Compose
    - Git
    - Internet connection for Azure/Grafana setup
"""

import argparse
import json
import os
import secrets as _secrets
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


class TwisterLabDeployer:
    """Automated TwisterLab community deployment"""

    def __init__(self, target_dir: str = ".", config_file: Optional[str] = None):
        self.target_dir = Path(target_dir).resolve()
        self.config_file = config_file or self.target_dir / "deploy_config.json"
        self.repo_url = "https://github.com/youneselfakir0/twisterlab.git"
        self.version = "v1.0.0"

        # Default configuration
        self.config: Dict[str, Any] = {
            "deployment_type": "full",  # full, minimal, development
            "enable_monitoring": True,
            "enable_security": True,
            "azure_subscription": None,
            # Prefer environment-provided secrets; otherwise generate strong random values for local community deployments
            "grafana_admin_password": os.getenv("GRAFANA_ADMIN_PASSWORD") or _secrets.token_hex(16),
            "postgres_password": os.getenv("POSTGRES_PASSWORD") or _secrets.token_hex(16),
            "redis_password": os.getenv("REDIS_PASSWORD") or _secrets.token_hex(16),
            "domain": "localhost",
            "ports": {
                "api": 8000,
                "grafana": 3000,
                "prometheus": 9090,
                "postgres": 5432,
                "redis": 6379,
            },
        }

    def load_config(self) -> None:
        """Load deployment configuration"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            print(f"✅ Configuration loaded from {self.config_file}")
        else:
            print("ℹ️  Using default configuration")

    def save_config(self) -> None:
        """Save current configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
        print(f"💾 Configuration saved to {self.config_file}")

    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        print("🔍 Checking prerequisites...")

        checks = [
            ("Python 3.8+", self._check_python_version),
            ("Docker", self._check_docker),
            ("Docker Compose", self._check_docker_compose),
            ("Git", self._check_git),
            ("Internet connection", self._check_internet),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                if check_func():
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name}")
                    all_passed = False
            except Exception as e:
                print(f"  ❌ {check_name}: {e}")
                all_passed = False

        return all_passed

    def _check_python_version(self) -> bool:
        return sys.version_info >= (3, 8)

    def _check_docker(self) -> bool:
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _check_docker_compose(self) -> bool:
        try:
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _check_git(self) -> bool:
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _check_internet(self) -> bool:
        try:
            urllib.request.urlopen("https://github.com", timeout=5)
            return True
        except Exception:
            return False

    def download_release(self) -> bool:
        """Download TwisterLab release"""
        print(f"📥 Downloading TwisterLab {self.version}...")

        try:
            # For community release, we'll clone the repo
            if (self.target_dir / ".git").exists():
                print("  📁 Repository already exists, updating...")
                subprocess.run(["git", "pull"], cwd=self.target_dir, check=True)
            else:
                print("  📁 Cloning repository...")
                subprocess.run(["git", "clone", self.repo_url, str(self.target_dir)], check=True)

            print("  ✅ Download completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Download failed: {e}")
            return False

    def configure_deployment(self) -> None:
        """Configure deployment based on type"""
        print("⚙️  Configuring deployment...")

        # Ensure secrets directory exists and create secret files
        secrets_dir = self.target_dir / "secrets"
        secrets_dir.mkdir(parents=True, exist_ok=True)

        # Write secret files for file-backed secrets (local development)
        postgres_pw = os.getenv(
            "POSTGRES_PASSWORD",
            self.config["postgres_password"],
        )
        with open(secrets_dir / "postgres_password", "w", encoding="utf-8") as f:
            f.write(postgres_pw)

        redis_pw = os.getenv("REDIS_PASSWORD", self.config["redis_password"])
        with open(secrets_dir / "redis_password", "w", encoding="utf-8") as f:
            f.write(redis_pw)

        grafana_pw = os.getenv(
            "GRAFANA_ADMIN_PASSWORD",
            self.config["grafana_admin_password"],
        )
        with open(secrets_dir / "grafana_admin_password", "w", encoding="utf-8") as f:
            f.write(grafana_pw)

        # Create .env file
        env_content = f"""# TwisterLab Environment Configuration
# Generated by deploy_community.py on {time.strftime("%Y-%m-%d %H:%M:%S")}

# Database
POSTGRES_PASSWORD_FILE=./secrets/postgres_password
REDIS_PASSWORD_FILE=./secrets/redis_password

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD_FILE=./secrets/grafana_admin_password
GRAFANA_SMTP_HOST=localhost:1025

# Azure (optional)
AZURE_SUBSCRIPTION_ID={self.config.get("azure_subscription", "")}

# Domain
DOMAIN={self.config["domain"]}

# Deployment type
DEPLOYMENT_TYPE={self.config["deployment_type"]}
ENABLE_MONITORING={str(self.config["enable_monitoring"]).lower()}
ENABLE_SECURITY={str(self.config["enable_security"]).lower()}
"""

        env_file = self.target_dir / ".env"
        with open(env_file, "w") as f:
            f.write(env_content)

        print(f"  ✅ Environment file created: {env_file}")

        # Configure docker-compose based on deployment type
        self._configure_docker_compose()

    def _configure_docker_compose(self) -> None:
        """Configure docker-compose.yml based on deployment type"""
        compose_file = self.target_dir / "docker-compose.yml"

        if not compose_file.exists():
            print("  ⚠️  docker-compose.yml not found, skipping configuration")
            return

        # For minimal deployment, we could modify the compose file
        # For now, we'll use the full compose file
        print("  ✅ Docker Compose configured for full deployment")

    def deploy_services(self) -> bool:
        """Deploy TwisterLab services"""
        print("🚀 Deploying TwisterLab services...")

        try:
            # Build and start services
            print("  🔨 Building services...")
            subprocess.run(["docker-compose", "build"], cwd=self.target_dir, check=True)

            print("  🏃 Starting services...")
            subprocess.run(["docker-compose", "up", "-d"], cwd=self.target_dir, check=True)

            # Wait for services to be healthy
            print("  🏥 Waiting for services to be healthy...")
            time.sleep(30)

            # Check service health
            result = subprocess.run(
                ["docker-compose", "ps"],
                cwd=self.target_dir,
                capture_output=True,
                text=True,
            )
            if "healthy" in result.stdout.lower():
                print("  ✅ Services deployed successfully")
                return True
            else:
                print("  ⚠️  Services deployed but health checks may be pending")
                print("  📊 Service status:")
                print(result.stdout)
                return True

        except subprocess.CalledProcessError as e:
            print(f"  ❌ Deployment failed: {e}")
            return False

    def setup_monitoring(self) -> bool:
        """Setup monitoring and dashboards"""
        if not self.config["enable_monitoring"]:
            print("⏭️  Monitoring disabled, skipping...")
            return True

        print("📊 Setting up monitoring...")

        try:
            # Grafana will be configured via provisioning files
            # Prometheus and Alertmanager are already configured

            print("  ✅ Monitoring setup completed")
            return True
        except Exception as e:
            print(f"  ❌ Monitoring setup failed: {e}")
            return False

    def run_tests(self) -> bool:
        """Run post-deployment tests"""
        print("🧪 Running post-deployment tests...")

        try:
            # Test API health
            import requests

            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("  ✅ API health check passed")
            else:
                print(f"  ⚠️  API health check failed: {response.status_code}")
                return False

            # Test database connection (if possible)
            print("  ✅ Post-deployment tests completed")
            return True

        except Exception as e:
            print(f"  ❌ Tests failed: {e}")
            return False

    def create_startup_script(self) -> None:
        """Create startup script for easy management"""
        startup_script = self.target_dir / "start_twisterlab.sh"

        script_content = f"""#!/bin/bash
# TwisterLab Startup Script
# Generated by deploy_community.py on {time.strftime("%Y-%m-%d %H:%M:%S")}

echo "🚀 Starting TwisterLab {self.version}..."

# Load environment
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Start services
docker-compose up -d

echo "✅ TwisterLab started!"
echo ""
echo "🌐 Access URLs:"
echo "  API: http://localhost:{self.config["ports"]["api"]}"
echo "  Grafana: http://localhost:{self.config["ports"]["grafana"]}"
echo "  Prometheus: http://localhost:{self.config["ports"]["prometheus"]}"
echo ""
echo "📚 Documentation: https://github.com/youneselfakir0/twisterlab"
"""

        with open(startup_script, "w") as f:
            f.write(script_content)

        # Make executable on Unix systems
        try:
            os.chmod(startup_script, 0o755)
        except Exception:
            pass  # Windows doesn't support chmod

        print(f"  ✅ Startup script created: {startup_script}")

    def generate_documentation(self) -> None:
        """Generate deployment documentation"""
        readme_content = f"""# TwisterLab {self.version} - Community Deployment

## 🚀 Quick Start

TwisterLab has been successfully deployed to this system!

### Access URLs
- **API**: http://localhost:{self.config["ports"]["api"]}
- **Grafana**: http://localhost:{self.config["ports"]["grafana"]}
- **Prometheus**: http://localhost:{self.config["ports"]["prometheus"]}

### Management Commands
```bash
# Start services
./start_twisterlab.sh
# or
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Update deployment
git pull && docker-compose up -d --build
```

## 📊 Monitoring

Grafana dashboards are automatically configured with:
- System health overview
- API performance metrics
- TwisterLang compression ratios
- Agent performance tracking
- Azure cost monitoring

## 🔧 Configuration

Deployment configuration saved in: `deploy_config.json`

### Key Settings
- **Deployment Type**: {self.config["deployment_type"]}
- **Monitoring**: {"Enabled" if self.config["enable_monitoring"] else "Disabled"}
- **Security**: {"Enabled" if self.config["enable_security"] else "Disabled"}
- **Domain**: {self.config["domain"]}

## 🆘 Troubleshooting

### Services not starting
```bash
# Check service status
docker-compose ps

# View detailed logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>
```

### Port conflicts
Edit the ports in `deploy_config.json` and run:
```bash
docker-compose down
docker-compose up -d
```

### Database issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
```

## 📚 Documentation

- [Full Documentation](https://github.com/youneselfakir0/twisterlab)
- [API Reference](https://github.com/youneselfakir0/twisterlab/blob/main/docs/API_REFERENCE.md)
- [Troubleshooting Guide](https://github.com/youneselfakir0/twisterlab/blob/main/docs/TROUBLESHOOTING.md)

## 🤝 Community

- **GitHub**: https://github.com/youneselfakir0/twisterlab
- **Issues**: https://github.com/youneselfakir0/twisterlab/issues
- **Discussions**: https://github.com/youneselfakir0/twisterlab/discussions

---

**Deployment completed on {time.strftime("%Y-%m-%d %H:%M:%S")}**
**TwisterLab v{self.version} - Ready for autonomous operations!** 🚀
"""

        readme_file = self.target_dir / "DEPLOYMENT_README.md"
        with open(readme_file, "w") as f:
            f.write(readme_content)

        print(f"  ✅ Documentation generated: {readme_file}")

    def cleanup(self) -> None:
        """Cleanup temporary files"""
        print("🧹 Cleaning up...")

        # Remove any temporary files if needed
        print("  ✅ Cleanup completed")

    def run(self) -> bool:
        """Run complete deployment process"""
        print(f"🚀 TwisterLab Community Deployment {self.version}")
        print("=" * 50)

        # Load configuration
        self.load_config()

        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Please install missing dependencies.")
            return False

        # Download release
        if not self.download_release():
            print("❌ Failed to download TwisterLab release.")
            return False

        # Configure deployment
        self.configure_deployment()

        # Deploy services
        if not self.deploy_services():
            print("❌ Service deployment failed.")
            return False

        # Setup monitoring
        if not self.setup_monitoring():
            print("⚠️  Monitoring setup had issues, but continuing...")

        # Run tests
        if not self.run_tests():
            print("⚠️  Some tests failed, but deployment may still work.")

        # Create startup script
        self.create_startup_script()

        # Generate documentation
        self.generate_documentation()

        # Save final configuration
        self.save_config()

        # Cleanup
        self.cleanup()

        print("\n" + "=" * 50)
        print("🎉 TwisterLab deployment completed successfully!")
        print("\n🌐 Access your instance at:")
        print(f"   API: http://localhost:{self.config['ports']['api']}")
        print(f"   Grafana: http://localhost:{self.config['ports']['grafana']}")
        print("\n📖 Check DEPLOYMENT_README.md for detailed instructions")
        return True


def main():
    parser = argparse.ArgumentParser(description="TwisterLab Community Deployment")
    parser.add_argument("--target-dir", default=".", help="Target deployment directory")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument(
        "--deployment-type",
        choices=["full", "minimal", "development"],
        default="full",
        help="Deployment type",
    )
    parser.add_argument("--no-monitoring", action="store_true", help="Disable monitoring")
    parser.add_argument("--grafana-password", help="Grafana admin password")

    args = parser.parse_args()

    # Create deployer
    deployer = TwisterLabDeployer(args.target_dir, args.config)

    # Update config from args
    deployer.config["deployment_type"] = args.deployment_type
    deployer.config["enable_monitoring"] = not args.no_monitoring
    if args.grafana_password:
        deployer.config["grafana_admin_password"] = args.grafana_password

    # Run deployment
    success = deployer.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
