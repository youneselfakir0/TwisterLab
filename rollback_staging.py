#!/usr/bin/env python3
"""
TwisterLab Staging Rollback Script
===================================

Quickly rollback staging deployment in case of failures.

Usage:
    python rollback_staging.py [--keep-volumes]
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


class Colors:
    """ANSI color codes"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(message: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_step(message: str):
    """Print step message"""
    print(f"{Colors.OKBLUE}▶ {message}...{Colors.ENDC}")


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
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def backup_logs():
    """Backup container logs before rollback"""
    print_step("Backing up container logs")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path(f"logs/rollback_{timestamp}")
    log_dir.mkdir(parents=True, exist_ok=True)

    containers = [
        "twisterlab-api-staging",
        "twisterlab-postgres-staging",
        "twisterlab-redis-staging",
        "twisterlab-ollama-staging",
        "prometheus-staging",
        "grafana-staging",
    ]

    for container in containers:
        returncode, stdout, stderr = run_command(["docker", "logs", container], check=False)

        if returncode == 0:
            log_file = log_dir / f"{container}.log"
            log_file.write_text(stdout)
            print(f"  ✓ {container}: logs saved")
        else:
            print(f"  ⚠ {container}: no logs (container may not exist)")

    print_success(f"Logs backed up to {log_dir}")
    return log_dir


def stop_containers():
    """Stop all staging containers"""
    print_step("Stopping staging containers")

    returncode, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.staging.yml", "stop"], check=False
    )

    if returncode == 0:
        print_success("All containers stopped")
    else:
        print_warning("Some containers may not have stopped cleanly")

    return True


def remove_containers():
    """Remove staging containers"""
    print_step("Removing staging containers")

    returncode, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.staging.yml", "rm", "-f"], check=False
    )

    if returncode == 0:
        print_success("All containers removed")
    else:
        print_warning("Some containers may not have been removed")

    return True


def remove_volumes(keep_volumes: bool = False):
    """Remove staging volumes"""
    if keep_volumes:
        print_step("Keeping volumes (--keep-volumes flag)")
        print_warning("Data preserved in volumes")
        return True

    print_step("Removing staging volumes")
    print_warning("⚠️  This will DELETE all staging data!")

    response = input("Are you sure? Type 'yes' to confirm: ")
    if response.lower() != "yes":
        print_warning("Volume removal cancelled - data preserved")
        return True

    returncode, stdout, stderr = run_command(
        ["docker-compose", "-f", "docker-compose.staging.yml", "down", "-v"], check=False
    )

    if returncode == 0:
        print_success("All volumes removed")
    else:
        print_warning("Some volumes may not have been removed")

    return True


def remove_network():
    """Remove staging network"""
    print_step("Removing staging network")

    returncode, stdout, stderr = run_command(
        ["docker", "network", "rm", "twisterlab-staging-network"], check=False
    )

    if returncode == 0:
        print_success("Network removed")
    else:
        print_warning("Network may not exist or is still in use")

    return True


def show_status():
    """Show current Docker status"""
    print_step("Checking remaining resources")

    # Check containers
    returncode, stdout, stderr = run_command(
        ["docker", "ps", "-a", "--filter", "name=staging"], check=False
    )

    if "staging" in stdout:
        print_warning("Some staging containers still exist:")
        print(stdout)
    else:
        print_success("No staging containers found")

    # Check volumes
    returncode, stdout, stderr = run_command(
        ["docker", "volume", "ls", "--filter", "name=staging"], check=False
    )

    if "staging" in stdout:
        print_warning("Some staging volumes still exist:")
        print(stdout)
    else:
        print_success("No staging volumes found")


def main():
    """Main rollback orchestration"""
    parser = argparse.ArgumentParser(description="Rollback TwisterLab staging deployment")
    parser.add_argument(
        "--keep-volumes", action="store_true", help="Keep data volumes (preserve data)"
    )
    args = parser.parse_args()

    print_header("🔄 TWISTERLAB STAGING ROLLBACK")

    print_warning("This will stop and remove all staging containers")
    if not args.keep_volumes:
        print_warning("Data volumes will be DELETED unless --keep-volumes is used")

    response = input("\nContinue with rollback? (yes/no): ")
    if response.lower() != "yes":
        print_warning("Rollback cancelled")
        sys.exit(0)

    # Backup logs
    log_dir = backup_logs()

    # Rollback steps
    stop_containers()
    remove_containers()
    remove_volumes(keep_volumes=args.keep_volumes)
    remove_network()

    # Show status
    show_status()

    # Success message
    print_header("✅ ROLLBACK COMPLETE")

    print(f"{Colors.BOLD}What happened:{Colors.ENDC}")
    print(f"  ✅ All staging containers stopped and removed")

    if args.keep_volumes:
        print(f"  ✅ Data volumes preserved (use --keep-volumes=false to remove)")
    else:
        print(f"  ✅ All staging data removed")

    print(f"  ✅ Logs backed up to {log_dir}")

    print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
    print(f"  1. Review logs in {log_dir}")
    print(f"  2. Fix issues identified")
    print(f"  3. Re-run deployment: python deploy_staging.py")

    print(
        f"\n{Colors.OKGREEN}{Colors.BOLD}"
        f"✅ Staging environment rolled back successfully!{Colors.ENDC}\n"
    )


if __name__ == "__main__":
    main()
