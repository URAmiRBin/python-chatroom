# Python Chatroom

A simple python chatroom backend.
It uses no databases, but as long as the server is running, the history is stored.

> WARNING: The exceptions in this thing are handled poorly, so be a good boy and don't break it, we just want to chat!

## server.py

Run this with ``` python server.py ``` and you're ready to go.
The console logs all the requests.

This server uses **long polling** to have a real-time chatroom.

The authorization key used is some random gibberish and it'll be stored in a dictionary to remember users by.

## client.py

This is a client prototype and I used threading to do sending messages and receiving new ones parallel.

Run this with ``` python client.py ``` and enter your name to enter the chatroom.

> Type !q in chat to exit the chatroom gracefully, the way the gods intended.