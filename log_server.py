#!/usr/bin/env python3
"""
Simple HTTP server to view Octave logs.
Serves the index.html page and provides real-time log viewing.
"""

import http.server
import socketserver
import os
import json
from pathlib import Path
from urllib.parse import urlparse


PORT = 8000
LOG_FILE = Path("logs/txt.log")


class LogServerHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve logs and static files."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve index.html
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        elif parsed_path.path == '/api/logs':
            # Serve log content
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                if LOG_FILE.exists():
                    with open(LOG_FILE, 'r', encoding='utf-8') as f:
                        logs = f.read()
                    response = {
                        'success': True,
                        'logs': logs,
                        'lines': logs.count('\n')
                    }
                else:
                    response = {
                        'success': False,
                        'error': 'Log file not found',
                        'logs': '',
                        'lines': 0
                    }
            except Exception as e:
                response = {
                    'success': False,
                    'error': str(e),
                    'logs': '',
                    'lines': 0
                }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif parsed_path.path == '/api/clear':
            # Clear log file
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                if LOG_FILE.exists():
                    LOG_FILE.unlink()
                response = {'success': True, 'message': 'Logs cleared'}
            except Exception as e:
                response = {'success': False, 'error': str(e)}
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            # Serve other static files
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def log_message(self, format, *args):
        """Override to customize log messages."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server():
    """Start the HTTP server."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), LogServerHandler) as httpd:
        print(f"Log server running at http://localhost:{PORT}/")
        print(f"Serving logs from: {LOG_FILE.absolute()}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    run_server()
