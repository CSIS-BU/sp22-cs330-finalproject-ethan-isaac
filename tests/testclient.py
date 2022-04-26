# client.py
import asyncio
import socket

HOST = "127.0.0.1" 
PORT = 8888
BUFFER_SIZE = 1024

def send_message(message, s):
        message = message.encode()
        s.sendall(message)
        data = s.recv(BUFFER_SIZE)
        return data.decode()

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        game_state = {}
        player = 0
        game_code = input("Welcome to Heads Up Poker! Please enter your game code, or press enter to start a new game: ")
        if game_code == "":
            game_code = send_message("new_game", s)
            print(game_code)
        else:
            game_state = send_message("join_game ", s)
            print(game_state)

        data = s.recv(BUFFER_SIZE)
        print(data)


