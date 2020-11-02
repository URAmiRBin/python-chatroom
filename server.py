from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import string
import random

class Serv(BaseHTTPRequestHandler):
    users = {}

    def do_GET(self):
        if self.path == '/':
            print("LONG POLLING TO BE ADDED")
        else:
            try:
                query = urllib.parse.parse_qs(self.path[2:])
                username = query['user-name'][0]
                auth = self.generate_auth()
                self.users[auth] = username
                self.send_response(200)
                self.send_header("auth", auth)
                self.end_headers()
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Bad Request'))

    def do_POST(self):
        print(self.headers['User'])
        if self.headers['User'] in self.users:
            try:
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                print(post_body)
                self.send_response(200)
                self.end_headers()
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Bad Request'))
        else:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(bytes('Unauthorized'))

    def generate_auth(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

httpd = HTTPServer(('127.0.0.1', 8080), Serv)
httpd.serve_forever()