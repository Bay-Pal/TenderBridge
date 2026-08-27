"""
TenderBridge — Local Web Application Server
Serves the visual interactive sales dashboard and provides a live /api/refresh endpoint.

Usage:
    python3 app.py
    (Then open the URL printed in the terminal)
"""

import os
import sys
import json
import http.server
import socketserver
from urllib.parse import urlparse
import subprocess
import socket

DEFAULT_PORT = 8090
DASHBOARD_FILE = "leads_dashboard.html"


class TenderBridgeHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/dashboard", "/leads"):
            self.path = f"/{DASHBOARD_FILE}"
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/refresh":
            print("\n[API] 🔄 Live data refresh triggered from browser...")
            try:
                # Trigger pipeline run in Python
                res = subprocess.run([sys.executable, "main.py", "--no-contacts"], capture_output=True, text=True)
                print(res.stdout)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "status": "success",
                    "message": "Pipeline executed and dashboard refreshed successfully!"
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
            except Exception as e:
                print(f"[!] Error executing refresh: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def find_free_port(start_port=DEFAULT_PORT, max_attempts=20):
    """Finds the first available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    return start_port


def run_server(preferred_port=None):
    # Ensure dashboard is compiled first
    from src.dashboard_generator import generate_html_dashboard
    generate_html_dashboard()

    port = preferred_port if preferred_port else find_free_port(DEFAULT_PORT)

    socketserver.TCPServer.allow_reuse_address = True
    
    try:
        with socketserver.TCPServer(("", port), TenderBridgeHandler) as httpd:
            print("\n" + "=" * 66)
            print("  🚀 TenderBridge — Live Intelligence Server")
            print("=" * 66)
            print(f"  🌐 Dashboard URL: http://localhost:{port}")
            print(f"  🔄 1-Click Refresh Enabled directly from Browser")
            print(f"  Press Ctrl+C to stop the server")
            print("=" * 66 + "\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        # Fallback to automatic free port
        alt_port = find_free_port(port + 1)
        print(f"\nPort {port} busy, switching to http://localhost:{alt_port} ...")
        with socketserver.TCPServer(("", alt_port), TenderBridgeHandler) as httpd:
            print(f"  🌐 Dashboard URL: http://localhost:{alt_port}")
            httpd.serve_forever()


if __name__ == "__main__":
    p = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        p = int(sys.argv[1])
    run_server(p)
