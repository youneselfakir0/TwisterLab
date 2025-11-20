#!/usr/bin/env python3
"""
Flask test server - Alternative to FastAPI
"""

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def root():
    return jsonify({"message": "Flask API is running", "status": "ok", "framework": "flask"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    print("Starting Flask API on port 8005...")
    app.run(host="127.0.0.1", port=8005, debug=False)
