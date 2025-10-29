#!/usr/bin/env python3
"""
Simple HTTP server test
"""

import http.server
import socketserver
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"message": "Hello from simple HTTP server"}')

if __name__ == "__main__":
    logger.info("Starting simple HTTP server on port 8002...")
    try:
        with socketserver.TCPServer(("", 8002), SimpleHandler) as httpd:
            logger.info("Server started on http://127.0.0.1:8002")
            try:
                httpd.serve_forever()
            except Exception as e:
                logger.error(f"Server error: {e}")
                import traceback
                logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())