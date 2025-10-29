#!/usr/bin/env python3
"""
TwisterLab API Test Script
Tests the ticket management endpoints
"""

import requests
import pytest
from typing import Optional


BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("🩺 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✅ Health check passed")
    except Exception as e:
        pytest.fail(f"❌ Health check error: {e}")


def test_create_ticket() -> Optional[str]:
    """Test ticket creation"""
    print("🎫 Testing ticket creation...")
    ticket_data = {
        "subject": "Test ticket from API",
        "description": "This is a test ticket created via API",
        "priority": "high",
        "category": "software",
        "requestor_email": "test@example.com"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/tickets/",
            json=ticket_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            ticket = response.json()
            print("✅ Ticket created successfully")
            print(f"   ID: {ticket['id']}")
            print(f"   Status: {ticket['status']}")
            return ticket['id']
        else:
            print(f"❌ Ticket creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ticket creation error: {e}")
        return None


def _test_get_ticket(ticket_id: str) -> bool:
    """Test getting a ticket"""
    print(f"📋 Testing ticket retrieval (ID: {ticket_id})...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tickets/{ticket_id}")

        if response.status_code == 200:
            ticket = response.json()
            print("✅ Ticket retrieved successfully")
            print(f"   Subject: {ticket['subject']}")
            print(f"   Status: {ticket['status']}")
            return True
        else:
            print(f"❌ Ticket retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ticket retrieval error: {e}")
        return False


def test_list_tickets():
    """Test listing tickets"""
    print("📝 Testing ticket listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tickets/")

        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        tickets = response.json()
        print("✅ Tickets listed successfully")
        print(f"   Count: {len(tickets)}")
    except Exception as e:
        pytest.fail(f"❌ Ticket listing error: {e}")


def _test_update_ticket(ticket_id: str) -> bool:
    """Test updating a ticket"""
    print(f"✏️ Testing ticket update (ID: {ticket_id})...")
    update_data = {
        "status": "assigned",
        "category": "network"
    }

    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/tickets/{ticket_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            ticket = response.json()
            print("✅ Ticket updated successfully")
            print(f"   New status: {ticket['status']}")
            print(f"   New category: {ticket['category']}")
            return True
        else:
            print(f"❌ Ticket update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ticket update error: {e}")
        return False


def _test_resolve_ticket(ticket_id: str) -> bool:
    """Test resolving a ticket"""
    print(f"✅ Testing ticket resolution (ID: {ticket_id})...")
    try:
        url = f"{BASE_URL}/api/v1/tickets/{ticket_id}/resolve"
        params = {"resolution": "Issue resolved successfully"}
        response = requests.post(url, params=params)

        if response.status_code == 200:
            ticket = response.json()
            print("✅ Ticket resolved successfully")
            print(f"   Status: {ticket['status']}")
            print(f"   Resolution: {ticket['resolution']}")
            return True
        else:
            print(f"❌ Ticket resolution failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ticket resolution error: {e}")
        return False


def _test_close_ticket(ticket_id: str) -> bool:
    """Test closing a ticket"""
    print(f"🔒 Testing ticket closure (ID: {ticket_id})...")
    try:
        url = f"{BASE_URL}/api/v1/tickets/{ticket_id}/close"
        response = requests.post(url)

        if response.status_code == 200:
            ticket = response.json()
            print("✅ Ticket closed successfully")
            print(f"   Final status: {ticket['status']}")
            return True
        else:
            print(f"❌ Ticket closure failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ticket closure error: {e}")
        return False


def _test_delete_ticket(ticket_id: str) -> bool:
    """Test deleting a ticket"""
    print(f"🗑️ Testing ticket deletion (ID: {ticket_id})...")
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/tickets/{ticket_id}")

        if response.status_code == 200:
            print("✅ Ticket deleted successfully")
            return True
        else:
            print(f"❌ Ticket deletion failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ticket deletion error: {e}")
        return False


def main() -> None:
    """Run all API tests"""
    print("🚀 Starting TwisterLab API Tests")
    print("=" * 50)

    # Test health endpoint
    if not test_health():
        print("❌ API is not running. Please start the server first.")
        return

    print()

    # Test ticket lifecycle
    ticket_id = test_create_ticket()
    if not ticket_id:
        print("❌ Cannot continue tests without ticket creation")
        return

    print()

    _test_get_ticket(ticket_id)
    print()

    test_list_tickets()
    print()

    _test_update_ticket(ticket_id)
    print()

    _test_resolve_ticket(ticket_id)
    print()

    _test_close_ticket(ticket_id)
    print()

    _test_delete_ticket(ticket_id)
    print()

    print("🎉 All API tests completed!")


if __name__ == "__main__":
    main()