# File: log_server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, time

ROOT = os.getcwd()
LOGS = os.path.join(ROOT, 'logs')
os.makedirs(LOGS, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/api/logs':
            self.send_response(404); self.end_headers(); return
        length = int(self.headers.get('Content-Length','0'))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            msg = data.get('msg','')
            fname = f'log-{int(time.time()*1000)}.txt'
            with open(os.path.join(LOGS, fname), 'w') as f:
                f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} :: {msg}\n")
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok':True,'path':f'logs/{fname}'}).encode('utf-8'))
        except Exception as e:
            self.send_response(500); self.end_headers()
            self.wfile.write(json.dumps({'error':str(e)}).encode('utf-8'))

if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()