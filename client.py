# client.py
import socket
from time import sleep 
import json

HOST = "127.0.0.1" 
PORT = 8888
BUFFER_SIZE = 1024
game_state = {}
player = 0
game_code = ""

def send_message(message, s):
        message = message.encode()
        s.sendall(message)
        data = s.recv(BUFFER_SIZE)
        return data.decode()

def handle_action(action, s):
    # check
    if action == "c":
        game_state = send_message(str(game_code) + " check", s)
    # bet
    elif action == "b":
        # prompt for bet amount
        bet_amount = input("Enter bet amount: ")
        game_state = send_message(str(game_code) + " bet " + bet_amount, s)
        
    # call
    elif action == "a":
        game_state = send_message(str(game_code) + " call", s)
    # raise
    elif action == "r":
        pass
    # fold
    elif action == "f":
        game_state = send_message(str(game_code) + " fold", s)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    game_state = {}
    player = 0
    game_code = input("Welcome to Heads Up Poker! Please enter your game code, or press enter to start a new game: ")
    if game_code == "":
        game_code = send_message("new_game", s)
        print("Your Public Game Code is: " + game_code)
        # game_state = send_message("join_game" + game_code + " 1", s)
        player = 1
        game_state = json.loads(s.recv(BUFFER_SIZE).decode())
    else:
        game_state = json.loads(send_message("join_game " + game_code + " 2", s))
        player = 2


    while True:
        if(game_state["comment"]  and len(game_state["comment"]) > 0):
            print(game_state["comment"])

        print("Comment", game_state["comment"])

        turn = game_state["turn"]
        print("Player " + str(turn) + " is up")

        if turn == player:
            print("Your hand is: " + str(game_state["player_" + str(player) + "_hand"]))
            print("Your balance is: " + str(game_state["player_" + str(player) + "_balance"]))
            print("Your blind is: " + str(game_state["player_" + str(player) + "_blind"]))
            print("Your opponent's balance is: " + str(game_state["player_" + str(3 - player) + "_balance"]))
            print("Your opponent's blind is: " + str(game_state["player_" + str(3 - player) + "_blind"]))
            print("The pot is: " + str(game_state["pot_balance"]))
            print("The cards on the table are: " + str(game_state["throw_down_cards"]))
            print("Your turn!")
            allowed_options = ["check(c)", "bet(b)", "call(a)", "raise(r)", "fold(f)"]
            if game_state["pending_bet"] > 0:
                allowed_options = ["call(a) opponents bet of " + str(game_state["pending_bet"]), "raise(r)", "fold(f)"]
            print("\n\n Your options are: " + str(allowed_options))
            action = input("\n\nPlease enter your action: ")
            if game_state["pending_bet"] > 0:
                while action not in ["a", "r", "f"]:
                    action = input(str(action) + " is not a valid option. Please enter your action: ")
            else:
                while action not in ["a", "b", "c", "r", "f"]:
                    action = input(str(action) + " is not a valid option. Please enter your action: ")

            handle_action(action, s)
        else:
            game_state = json.loads(s.recv(BUFFER_SIZE).decode())


