from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import string
import random

# For handling requests in multiple threads
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

# Customized BaseHTTPRequestHandler
class Serv(BaseHTTPRequestHandler):
    # Dictionary of users auth to their names
    # Users will be removed after they left the chat
    users = {}
    # Handler for long polling requests
    # keys : user auth and values 0 (no new message) or 1 (has new message)
    queues = {}
    # messages log
    messages = []

    def do_GET(self):
        # GETTING MESSAGES LONG POLLING
        if self.path == '/':
            try:
                if self.headers['User'] in self.users:
                    # Wait till a new message comes
                    message = self.wait(self.headers['User'])
                    self.queues[self.headers['User']] = False

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(message.encode('utf-8'))
                    return
            except:
                print("UNAUTHORIZED ACCESS")
                self.send_response(401)
                self.end_headers()
                self.wfile.write(bytes('Unauthorized', 'utf-8'))
        # NEW LOGIN
        else:
            try:
                # Parse query
                query = urllib.parse.parse_qs(self.path[2:])
                username = query['user-name'][0]

                # Generate Auth code
                auth = self.generate_auth()
                self.users[auth] = username

                # Response with auth code
                self.send_response(200)
                self.send_header("auth", auth)
                self.end_headers()

                # Generate message history string
                log = ''
                for m in self.messages:
                    log += m
                    log += '\n'

                # Send message history
                self.wfile.write(log.encode('utf-8'))

                # Welcome message
                self.messages.append(username + " joined the chatroom!")
                print("NEW USER ", username, " : ", auth)

                # Set new messages for everyone else
                for key in self.queues:
                    self.queues[key] = True
                self.queues[auth] = False
                
            except:
                print("BAD REQUEST")
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Bad Request', 'utf-8'))

    def do_POST(self):
        # Sending message
        if self.headers['User'] in self.users:
            try:
                # Get request details
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                message = post_body.decode('utf-8')
                
                # Leave request
                if message == '!q':
                    print("USER LEFT : ", self.users[self.headers['User']])
                    self.messages.append(self.users[self.headers['User']] + " has left the chat!")
                    self.users.pop(self.headers['User'])
                    self.queues.pop(self.headers['User'])

                # Message
                else:
                    print("NEW MESSAGE FROM ", self.users[self.headers['User']])
                    self.messages.append(self.users[self.headers['User']] + ":" + message)
                    self.queues[self.headers['User']] = False

                # Set new message for everyone else
                for key in self.queues:
                    if key != self.headers['User']:
                        self.queues[key] = True

                # Send response
                self.send_response(200)
                self.end_headers()
            except:
                print("BAD REQUEST")
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Bad Request', 'utf-8'))
        else:
            print("UNAUTHORIZED ACCESS")
            self.send_response(401)
            self.end_headers()
            self.wfile.write(bytes('Unauthorized', 'utf-8'))


    # Vicious loop of waiting for a new message (long polling)
    def wait(self, key):
        while(not self.queues[key]):
            continue
        return self.messages[-1]

    # authorization code generator
    def generate_auth(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))


# Run Threaded HTTP Server
if __name__ == '__main__':
    server = ThreadedHTTPServer(('127.0.0.1', 8080), Serv)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
