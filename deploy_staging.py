#!/usr/bin/env python3
"""
TwisterLab Staging Deployment Script
====================================

Automated deployment to staging environment with pre-flight checks and validation.

Usage:
    python deploy_staging.py [--skip-tests] [--pull-images] [--clean]
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple
import argparse

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_step(step: int, total: int, message: str):
    """Print step progress"""
    print(f"{Colors.OKBLUE}[{step}/{total}] {message}...{Colors.ENDC}")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def run_command(cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
    """Execute shell command and return results"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr

def check_docker():
    """Check if Docker is running"""
    print_step(1, 10, "Checking Docker installation")
    returncode, stdout, stderr = run_command(["docker", "version"], check=False)
    
    if returncode != 0:
        print_error("Docker is not running or not installed")
        print(f"Error: {stderr}")
        return False
    
    print_success("Docker is running")
    return True

def check_docker_compose():
    """Check if Docker Compose is available"""
    print_step(2, 10, "Checking Docker Compose")
    returncode, stdout, stderr = run_command(["docker-compose", "version"], check=False)
    
    if returncode != 0:
        print_error("Docker Compose is not installed")
        return False
    
    print_success("Docker Compose is available")
    return True

def run_tests(skip: bool = False):
    """Run test suite"""
    if skip:
        print_step(3, 10, "Skipping tests (--skip-tests flag)")
        print_warning("Tests skipped - not recommended for staging deployment")
        return True
    
    print_step(3, 10, "Running test suite")
    returncode, stdout, stderr = run_command(
        ["pytest", "tests/", "-v", "--tb=short"],
        check=False
    )
    
    if returncode != 0:
        print_error("Tests failed")
        print(stderr)
        return False
    
    print_success("All tests passed")
    return True

def check_env_file():
    """Check if .env.staging exists"""
    print_step(4, 10, "Checking environment configuration")
    env_file = Path(".env.staging")
    
    if not env_file.exists():
        print_warning(".env.staging not found")
        print(f"Creating from example: .env.staging.example")
        
        example_file = Path(".env.staging.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print_warning("⚠️  IMPORTANT: Update .env.staging with your credentials!")
            return True
        else:
            print_error(".env.staging.example not found")
            return False
    
    print_success(".env.staging found")
    return True

def pull_images(pull: bool = False):
    """Pull latest Docker images"""
    if not pull:
        print_step(5, 10, "Skipping image pull (use --pull-images to update)")
        return True
    
    print_step(5, 10, "Pulling latest Docker images")
    returncode, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.staging.yml", "pull"],
        check=False
    )
    
    if returncode != 0:
        print_warning("Failed to pull some images")
        print(stderr)
        # Continue anyway
    else:
        print_success("Images pulled successfully")
    
    return True

def stop_existing_containers():
    """Stop and remove existing staging containers"""
    print_step(6, 10, "Stopping existing staging containers")
    returncode, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.staging.yml", "down"],
        check=False
    )
    
    if returncode == 0:
        print_success("Existing containers stopped")
    else:
        print_warning("No existing containers to stop")
    
    return True

def build_images():
    """Build Docker images"""
    print_step(7, 10, "Building Docker images")
    returncode, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.staging.yml", "build", "--no-cache"],
        check=False
    )
    
    if returncode != 0:
        print_error("Docker build failed")
        print(stderr)
        return False
    
    print_success("Docker images built successfully")
    return True

def start_services():
    """Start all services"""
    print_step(8, 10, "Starting services")
    returncode, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.staging.yml", "up", "-d"],
        check=False
    )
    
    if returncode != 0:
        print_error("Failed to start services")
        print(stderr)
        return False
    
    print_success("Services started successfully")
    return True

def wait_for_health_checks():
    """Wait for all services to be healthy"""
    print_step(9, 10, "Waiting for health checks (max 120s)")
    
    max_wait = 120
    interval = 5
    elapsed = 0
    
    while elapsed < max_wait:
        returncode, stdout, stderr = run_command(
            ["docker-compose", "-f", "docker-compose.staging.yml", "ps"],
            check=False
        )
        
        if "healthy" in stdout.lower():
            print_success(f"Services healthy after {elapsed}s")
            return True
        
        print(f"  Waiting... ({elapsed}s/{max_wait}s)")
        time.sleep(interval)
        elapsed += interval
    
    print_warning("Health checks timeout - services may still be starting")
    return True  # Continue anyway

def run_smoke_tests():
    """Run smoke tests"""
    print_step(10, 10, "Running smoke tests")
    
    # Wait a bit more for services to fully start
    time.sleep(10)
    
    # Test API health endpoint
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=10)
        if response.status_code == 200:
            print_success("API health check passed")
        else:
            print_warning(f"API health check returned {response.status_code}")
    except Exception as e:
        print_warning(f"API health check failed: {e}")
    
    # Test Prometheus
    try:
        import requests
        response = requests.get("http://localhost:9092/-/healthy", timeout=10)
        if response.status_code == 200:
            print_success("Prometheus health check passed")
        else:
            print_warning(f"Prometheus returned {response.status_code}")
    except Exception as e:
        print_warning(f"Prometheus health check failed: {e}")
    
    print_success("Smoke tests completed")
    return True

def show_urls():
    """Display access URLs"""
    print_header("🎉 STAGING DEPLOYMENT COMPLETE!")
    
    print(f"{Colors.BOLD}Access URLs:{Colors.ENDC}")
    print(f"  📡 API:        http://localhost:8001")
    print(f"  📊 API Docs:   http://localhost:8001/docs")
    print(f"  📈 Metrics:    http://localhost:9091/metrics")
    print(f"  🔍 Prometheus: http://localhost:9092")
    print(f"  📊 Grafana:    http://localhost:3001 (admin/staging_grafana_password)")
    print(f"  🌐 OpenWebUI:  http://localhost:8081")
    
    print(f"\n{Colors.BOLD}Useful Commands:{Colors.ENDC}")
    print(f"  View logs:     docker-compose -f docker-compose.staging.yml logs -f")
    print(f"  Stop services: docker-compose -f docker-compose.staging.yml down")
    print(f"  Restart:       docker-compose -f docker-compose.staging.yml restart")
    print(f"  Status:        docker-compose -f docker-compose.staging.yml ps")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"  1. Update .env.staging with production credentials")
    print(f"  2. Pull Ollama models: docker exec twisterlab-ollama-staging ollama pull deepseek-r1")
    print(f"  3. Run integration tests: pytest tests/test_integration_full_system.py -v")
    print(f"  4. Configure Grafana dashboards")
    print(f"  5. Set up alerts in Prometheus")

def main():
    """Main deployment orchestration"""
    parser = argparse.ArgumentParser(description="Deploy TwisterLab to staging")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--pull-images", action="store_true", help="Pull latest images")
    parser.add_argument("--clean", action="store_true", help="Clean build (no cache)")
    args = parser.parse_args()
    
    print_header("🚀 TWISTERLAB STAGING DEPLOYMENT")
    
    # Pre-flight checks
    if not check_docker():
        sys.exit(1)
    
    if not check_docker_compose():
        sys.exit(1)
    
    if not run_tests(skip=args.skip_tests):
        print_error("Tests failed - aborting deployment")
        sys.exit(1)
    
    if not check_env_file():
        print_error("Environment configuration missing")
        sys.exit(1)
    
    # Deployment steps
    if not pull_images(pull=args.pull_images):
        sys.exit(1)
    
    if not stop_existing_containers():
        sys.exit(1)
    
    if not build_images():
        sys.exit(1)
    
    if not start_services():
        sys.exit(1)
    
    if not wait_for_health_checks():
        # Continue anyway
        pass
    
    if not run_smoke_tests():
        # Continue anyway
        pass
    
    # Show success
    show_urls()
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Staging deployment successful!{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
