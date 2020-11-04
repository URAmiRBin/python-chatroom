import requests
import logging
import threading
import sys

# SETTINGS
URL = 'http://127.0.0.1:8080'
USERNAME = input("Enter you name >").encode('utf-8')
SESSION = requests.Session()

# Thread for sending messages
def client_send():
    message = ""
    # !q is the command for exit
    while(message != "!q".encode('utf-8')):
        message = input().encode('utf-8')
        try:
            # Send post request with auth header and message body
            # Content length is automatically created by the library
            SESSION.post(URL, headers = {'User' : AUTH}, data = message)
        except Exception as e:
            print(e)
            sys.exit()


def client_recv():
    while(True):
        try:
            # Receive get request with auth header
            response = SESSION.get(URL, headers = {'User' : AUTH})
            if response.status_code != 200:
                print(response.status_code, " : ", response.text)
                sys.exit()
            print(response.text)
        except Exception as e:
            print(e)
            sys.exit()


try:
    # Login get request : 127.0.0.1:8080/?user-name=USERNAME
    response = SESSION.get(URL, params={'user-name': USERNAME})
except:
    print('Client Error : Server ', URL, ' did not respond')
    sys.exit()
else:
    if response.status_code != 200:
        print(response.status_code, " : ", response.text)
        sys.exit()
    # Get Authorization code from server
    AUTH = response.headers['auth'].encode('utf-8')
    print("Welcome to chatroom! type !q to leave")
    # Server returns message log in response body
    print(response.text)

# Run two parallel threads, one for sending and another for receiving
receive_thread = threading.Thread(target=client_recv)
receive_thread.start()

write_thread = threading.Thread(target=client_send)
write_thread.start()