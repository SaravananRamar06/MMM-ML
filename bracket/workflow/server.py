"""Local web page for the porosity material study and solver-results comparison (http://127.0.0.1:8767)."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import porosity_workflow as pw

HERE = Path(__file__).resolve().parent
LIMITS = {'/api/porosity-study': 65536, '/api/solver-results': 1048576}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, kind='application/json'):
        data = body if isinstance(body, bytes) else json.dumps(body, allow_nan=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ('/', '/workflow', '/workflow.html'):
            self._send(200, (HERE / 'workflow.html').read_bytes(), 'text/html; charset=utf-8')
        elif self.path == '/api/workflow':
            self._send(200, pw.readiness())
        elif self.path == '/api/health':
            self._send(200, {'ok': True})
        else:
            self._send(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path not in LIMITS:
            return self._send(404, {'error': 'Not found'})
        n = int(self.headers.get('Content-Length', 0))
        if n < 0 or n > LIMITS[self.path]:
            return self._send(413, {'error': 'Request too large.'})
        try:
            body = json.loads(self.rfile.read(n) or b'{}')
            if self.path == '/api/porosity-study':
                result = pw.material_study(body.get('mapping'), body.get('phi_values'), body.get('temperature_C'),
                                           body.get('strain_rate_s'), allow_assumed=bool(body.get('allow_assumed')))
            else:
                result = pw.compare_solver_results(str(body.get('csv', '')))
            self._send(200, result)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, {'error': str(exc)})

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    port = int(os.environ.get('WORKFLOW_PORT', '8767'))
    print(f'Porosity workflow at http://127.0.0.1:{port}')
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
