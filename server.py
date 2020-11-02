from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from threading import Thread
import urllib.parse
import string
import random
import json

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Serv(BaseHTTPRequestHandler):
    users = {}
    queues = {}
    messages = []

    def do_GET(self):
        if self.path == '/':
            try:
                if self.headers['User'] in self.users:
                    self.send_response(200)
                    self.end_headers()
                    print(self.headers)
                    message = self.wait(self.headers['User'])
                    self.queues[self.headers['User']] = False
                    self.wfile.write(message.encode('utf-8'))
                    self.wfile.write('\n'.encode('utf-8'))
                    return
            except:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(bytes('Unauthorized', 'utf-8'))
        else:
            try:
                query = urllib.parse.parse_qs(self.path[2:])
                username = query['user-name'][0]
                auth = self.generate_auth()
                self.users[auth] = username
                self.send_response(200)
                self.send_header("auth", auth)
                self.end_headers()
                log = ''
                for m in self.messages:
                    log += m
                    log += '\n'
                print("OLD MESSAGES ", log)
                self.wfile.write(log.encode('utf-8'))
                self.messages.append(username + " joined the chatroom!")
                
                for key in self.queues:
                    self.queues[key] = True
                self.queues[auth] = False
                
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Bad Request', 'utf-8'))

    def do_POST(self):
        print(self.headers['User'])
        if self.headers['User'] in self.users:
            try:
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                message = post_body.decode('utf-8')
                print(message)
                if message == '!q':
                    self.messages.append(self.users[self.headers['User']] + " has left the chat!")
               
               
                    self.users.pop(self.headers['User'])
                    self.queues.pop(self.headers['User'])
                else:
                    self.messages.append(self.users[self.headers['User']] + ":" + message)
                    self.queues[self.headers['User']] = False

                for key in self.queues:
                    if key != self.headers['User']:
                        self.queues[key] = True


                self.send_response(200)
                self.end_headers()
                print(self.users)
                print(self.messages)
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes('Bad Request', 'utf-8'))
        else:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(bytes('Unauthorized', 'utf-8'))


    def wait(self, key):
        try:
            while(not self.queues[key]):
                continue
            return self.messages[-1]
        except:
            return bytes('Unauthorized', 'utf-8')

    def generate_auth(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))


if __name__ == '__main__':
    server = ThreadedHTTPServer(('localhost', 8080), Serv)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
