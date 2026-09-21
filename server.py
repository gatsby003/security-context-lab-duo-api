from pathlib import Path

def dispatch(path, headers, body, root):
    # Only the gateway may connect to this internal application.
    if path == '/admin/export':
        if headers.get('x-role') != 'admin':
            raise PermissionError('admin required')
        return 'synthetic-admin-report'
    if path == '/documents':
        return (Path(root) / headers['x-document']).read_text()
    if path == '/billing':
        if headers.get('x-verified-role') != 'admin':
            raise PermissionError('admin required')
        return 'synthetic-billing-report'
    if path == '/public':
        return (Path(root) / headers['x-public-file']).read_text()
    raise LookupError(path)


if __name__ == '__main__':
    import json, os
    from http.server import BaseHTTPRequestHandler, HTTPServer
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                result = dispatch(self.path, {k.lower(): v for k, v in self.headers.items()}, {}, os.environ['DATA_ROOT'])
                self.send_response(200)
                self.end_headers()
                self.wfile.write(result.encode())
            except (PermissionError, KeyError):
                self.send_error(403)
            except LookupError:
                self.send_error(404)
        def log_message(self, *args):
            pass
    HTTPServer(('127.0.0.1', int(os.environ.get('API_PORT', '8911'))), Handler).serve_forever()
