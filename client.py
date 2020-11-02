import requests
import logging
from requests.exceptions import HTTPError
import threading

URL = 'http://127.0.0.1:8080'
s = requests.Session()
username = input("enter you name >").encode('utf-8')

try:
    response = s.get(URL, params={'user-name': username})

    response.raise_for_status()
except:
    print('ERROR')
else:
    myauth = response.headers['auth'].encode('utf-8')

def client_send():
    message = ""
    while(message != "!q".encode('utf-8')):
        message = input(">").encode('utf-8')
        message_length = str(len(message))
        try:
            response = s.post(URL, headers = {'User' : myauth, 'Content-Length' : message_length}, data = message)
            if response.status_code != 200:
                break
            print(response.text)
            response.raise_for_status()
        except Exception as e:
            print(e)
            print("ERROR")
            break

def client_recv():
    while(True):
        try:
            response = s.get(URL, headers = {'User' : myauth})
            if response.status_code != 200:
                break
            print(response.text)
            response.raise_for_status()
        except Exception as e:
            print(e)
            print("ERROR")
            break


receive_thread = threading.Thread(target=client_recv)
receive_thread.start()

write_thread = threading.Thread(target=client_send)
write_thread.start()