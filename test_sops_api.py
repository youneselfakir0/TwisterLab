"""
Test script for TwisterLab SOPs API with PostgreSQL database.

Tests:
1. Database connection
2. API endpoints (CRUD operations on SOPs)
3. Data validation
"""

from datetime import datetime
from typing import Optional

import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{RED}✗{RESET} {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{YELLOW}ℹ{RESET} {text}")


def test_health() -> bool:
    """Test health/hello endpoint."""
    print_header("TEST 1: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/sops/hello", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_success("API is running!")
            print_info(f"Response: {data}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is it running?")
        print_info("Start API with: uvicorn agents.api.main:app --reload")
        return False
    except requests.RequestException as e:
        print_error(f"Health check error: {str(e)}")
        return False


from typing import Optional


def test_create_sop() -> Optional[str]:
    """Test creating a new SOP."""
    print_header("TEST 2: Create SOP")

    sop_data = {
        "title": "Password Reset Procedure",
        "description": "Standard procedure for resetting user passwords in Active Directory",
        "category": "password",
        "steps": [
            "1. Verify user identity (check employee ID or ask security questions)",
            "2. Open Active Directory Users and Computers",
            "3. Locate the user account",
            "4. Right-click on user → Reset Password",
            "5. Generate temporary password (min 12 chars)",
            "6. Check 'User must change password at next logon'",
            "7. Notify user via email with temporary password",
            "8. Log the action in the ticket system",
        ],
        "applicable_issues": [
            "password_reset",
            "forgot_password",
            "account_locked",
            "password_expired",
        ],
        "estimated_time": 5,
        "success_rate": 0.98,
        "tags": ["password", "active-directory", "security"],
    }

    try:
        response = requests.post(f"{BASE_URL}/sops/", json=sop_data, timeout=10)

        if response.status_code == 201:
            created_sop = response.json()
            print_success("SOP created successfully!")
            print_info(f"SOP ID: {created_sop['id']}")
            print_info(f"Title: {created_sop['title']}")
            print_info(f"Steps: {len(created_sop['steps'])}")
            return created_sop["id"]
        else:
            print_error(f"Failed to create SOP: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None

    except requests.RequestException as e:
        print_error(f"Error creating SOP: {str(e)}")
        return None


def test_list_sops() -> bool:
    """Test listing all SOPs."""
    print_header("TEST 3: List SOPs")

    try:
        response = requests.get(f"{BASE_URL}/sops/", timeout=10)

        if response.status_code == 200:
            sops = response.json()
            print_success(f"Retrieved {len(sops)} SOP(s)")

            for sop in sops:
                print_info(f"  - [{sop['id']}] {sop['title']} ({sop['category']})")

            return len(sops) > 0
        else:
            print_error(f"Failed to list SOPs: {response.status_code}")
            return False

    except requests.RequestException as e:
        print_error(f"Error listing SOPs: {str(e)}")
        return False


def _test_get_sop(sop_id: str) -> bool:
    """Test retrieving a specific SOP."""
    print_header(f"TEST 4: Get SOP by ID ({sop_id})")

    if not sop_id:
        print_error("No SOP ID provided (skip test)")
        return False

    try:
        response = requests.get(f"{BASE_URL}/sops/{sop_id}", timeout=10)

        if response.status_code == 200:
            sop = response.json()
            print_success("SOP retrieved successfully!")
            print_info(f"Title: {sop['title']}")
            print_info(f"Category: {sop['category']}")
            print_info(f"Steps: {len(sop['steps'])}")
            print_info(f"Estimated time: {sop.get('estimated_time', 'N/A')} minutes")
            print_info(f"Success rate: {sop.get('success_rate', 'N/A')}")
            return True
        elif response.status_code == 404:
            print_error(f"SOP {sop_id} not found")
            return False
        else:
            print_error(f"Failed to get SOP: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error getting SOP: {str(e)}")
        return False


def _test_update_sop(sop_id: str) -> bool:
    """Test updating a SOP."""
    print_header(f"TEST 5: Update SOP ({sop_id})")

    if not sop_id:
        print_error("No SOP ID provided (skip test)")
        return False

    update_data = {
        "description": "UPDATED: Standard procedure for resetting user passwords in Active Directory",
        "estimated_time": 7,
        "tags": ["password", "active-directory", "security", "updated"],
    }

    try:
        response = requests.put(f"{BASE_URL}/sops/{sop_id}", json=update_data, timeout=10)

        if response.status_code == 200:
            updated_sop = response.json()
            print_success("SOP updated successfully!")
            print_info(f"New description: {updated_sop['description'][:50]}...")
            print_info(f"New estimated time: {updated_sop['estimated_time']} minutes")
            return True
        else:
            print_error(f"Failed to update SOP: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error updating SOP: {str(e)}")
        return False


def _test_delete_sop(sop_id: str) -> bool:
    """Test deleting a SOP."""
    print_header(f"TEST 6: Delete SOP ({sop_id})")

    if not sop_id:
        print_error("No SOP ID provided (skip test)")
        return False

    try:
        response = requests.delete(f"{BASE_URL}/sops/{sop_id}", timeout=10)

        if response.status_code == 204:
            print_success("SOP deleted successfully!")
            return True
        elif response.status_code == 404:
            print_error(f"SOP {sop_id} not found")
            return False
        else:
            print_error(f"Failed to delete SOP: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error deleting SOP: {str(e)}")
        return False


def test_search_by_category() -> bool:
    """Test searching SOPs by category."""
    print_header("TEST 7: Search by Category")

    try:
        response = requests.get(f"{BASE_URL}/sops/", params={"category": "password"}, timeout=10)

        if response.status_code == 200:
            sops = response.json()
            print_success(f"Found {len(sops)} SOP(s) in 'password' category")

            for sop in sops:
                print_info(f"  - {sop['title']}")

            return True
        else:
            print_error(f"Failed to search SOPs: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error searching SOPs: {str(e)}")
        return False


def main() -> None:
    """Run all tests."""
    print(f"\n{BLUE}{'*' * 60}")
    print("  TwisterLab SOPs API Test Suite")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'*' * 60}{RESET}\n")

    results = {"total": 0, "passed": 0, "failed": 0}

    # Test 1: Health check
    results["total"] += 1
    if test_health():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("\nAPI is not running. Cannot continue tests.")
        print_info("Start API with: uvicorn agents.api.main:app --reload")
        return

    # Test 2: Create SOP
    results["total"] += 1
    sop_id = test_create_sop()
    if sop_id:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 3: List SOPs
    results["total"] += 1
    if test_list_sops():
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 4: Get SOP by ID
    results["total"] += 1
    if sop_id is not None and _test_get_sop(sop_id):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 5: Update SOP
    results["total"] += 1
    if sop_id is not None and _test_update_sop(sop_id):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 7: Search by category
    results["total"] += 1
    if test_search_by_category():
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 6: Delete SOP (last to cleanup)
    results["total"] += 1
    if sop_id is not None and _test_delete_sop(sop_id):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Print summary
    print_header("TEST SUMMARY")
    print(f"Total tests: {results['total']}")
    print(f"{GREEN}Passed: {results['passed']}{RESET}")
    print(f"{RED}Failed: {results['failed']}{RESET}")

    success_rate = (results["passed"] / results["total"]) * 100
    print(f"\n{BLUE}Success rate: {success_rate:.1f}%{RESET}")

    if results["failed"] == 0:
        print(f"\n{GREEN}{'🎉 ' * 10}")
        print("  ALL TESTS PASSED!")
        print(f"{'🎉 ' * 10}{RESET}\n")
    else:
        print(f"\n{YELLOW}Some tests failed. Check the output above.{RESET}\n")


if __name__ == "__main__":
    main()
