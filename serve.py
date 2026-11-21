"""Simple static file server for KnightScope HTML/CSS/JS application.
Serves index.html as the root, used by Render for deployment.
"""
import http.server
import socketserver
import os

PORT = int(os.environ.get("PORT", 8080))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Serve index.html for root
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        return super().do_GET()


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"KnightScope serving on port {PORT}")
    httpd.serve_forever()
