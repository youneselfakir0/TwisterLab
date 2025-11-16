#!/usr/bin/env python3
"""
TwisterLab Flask API - Temporary alternative for testing
"""

import asyncio
import sys
from pathlib import Path

from flask import Flask, jsonify, request

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

app = Flask(__name__)


@app.route("/")
def root():
    """Root endpoint"""
    return jsonify(
        {
            "name": "TwisterLab Flask API",
            "description": "Temporary Flask version for testing",
            "version": "1.0.0-test",
            "docs": "/docs",
            "health": "/health",
        }
    )


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "framework": "flask", "database": "testing"})


@app.route("/api/v1/tickets", methods=["GET", "POST"])
def tickets():
    """Tickets endpoint"""
    if request.method == "GET":
        return jsonify({"tickets": [], "total": 0, "message": "Flask API - tickets endpoint"})
    else:
        return jsonify({"message": "Ticket created (mock)", "id": "test-123"})


@app.route("/api/v1/agents", methods=["GET"])
def agents():
    """Agents endpoint"""
    return jsonify(
        {
            "agents": [
                {"id": "classifier", "name": "Ticket Classifier", "status": "active"},
                {"id": "resolver", "name": "Helpdesk Resolver", "status": "active"},
            ],
            "message": "Flask API - agents endpoint",
        }
    )


@app.route("/api/v1/sops", methods=["GET"])
def sops():
    """SOPs endpoint"""
    return jsonify({"sops": [], "total": 0, "message": "Flask API - SOPs endpoint"})


@app.route("/docs")
def docs():
    """API documentation"""
    return jsonify(
        {
            "message": "API Documentation",
            "endpoints": [
                "GET /",
                "GET /health",
                "GET /api/v1/tickets",
                "POST /api/v1/tickets",
                "GET /api/v1/agents",
                "GET /api/v1/sops",
            ],
        }
    )


if __name__ == "__main__":
    print("Starting TwisterLab Flask API on port 8000...")
    print("This is a temporary Flask version for testing purposes")
    app.run(host="0.0.0.0", port=8000, debug=False)
