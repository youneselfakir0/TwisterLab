#!/usr/bin/env python3
"""Test Redis and Ollama connectivity from API container."""

import socket
import sys

def test_connection(host: str, port: int, service_name: str) -> bool:
    """Test TCP connection to a service."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        s.close()
        print(f"✅ {service_name}: Connection successful to {host}:{port}")
        return True
    except Exception as e:
        print(f"❌ {service_name}: Connection failed to {host}:{port} - {e}")
        return False

if __name__ == "__main__":
    results = []

    # Test Redis
    results.append(test_connection("redis", 6379, "Redis"))

    # Test Ollama
    results.append(test_connection("ollama", 11434, "Ollama"))

    # Test PostgreSQL
    results.append(test_connection("postgres", 5432, "PostgreSQL"))

    if all(results):
        print("\n✅ ALL SERVICES ACCESSIBLE")
        sys.exit(0)
    else:
        print("\n❌ SOME SERVICES UNREACHABLE")
        sys.exit(1)
