# client.py
import socket
import json
from time import sleep

# card suits
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

# royal cards
ROYAL = ["Jack", "Queen", "King", "Ace"]

HOST = "127.0.0.1" 
PORT = 8088
BUFFER_SIZE = 1024
game_state = {}
player = 0
game_code = ""

def get_card_suit(card):
    return SUITS[card[0]]

def get_card_value(card):
    if card[1] == 1:
        return ROYAL[3]
    elif card[1] in [11, 12, 13]:
        return ROYAL[card[1] - 11]
    else:
        return card[1]

# print deck of cards with suits and ranks
def print_deck(deck):
    print("")
    for card in deck:
        print("     [", get_card_value(card), " of ",get_card_suit(card) ,"]")
    
    print("")

def send_message(message, s):
        message = message.encode()
        s.sendall(message)
        data = s.recv(BUFFER_SIZE)
        return data.decode()

def handle_action(action, s, game_state, player):
    # check
    if action == "c":
        return send_message(str(game_code) + " check", s)
    # bet
    elif action == "b":
        # prompt for bet amount
        bet_amount = input("Enter bet amount: ")
        while int(bet_amount) > game_state["player_" + str(player) + "_balance"]:
            bet_amount = input("Bet amount exceeds available balance. Enter bet amount: ")
        return send_message(str(game_code) + " bet " + bet_amount, s)
        
    # call
    elif action == "a":
        return send_message(str(game_code) + " call", s)
    # raise
    elif action == "r":
        # prompt for raise amount
        raise_amount = input("Enter what you would like to raise by: ")
        while int(raise_amount) > game_state["player_" + str(player) + "_balance"] - game_state["pending_bet"]:
            raise_amount = input("Raise amount exceeds available balance. Enter raise amount: ")
        return send_message(str(game_code) + " raise " + raise_amount, s)
    # fold
    elif action == "f":
        return send_message(str(game_code) + " fold", s)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    game_state = {}
    player = 0
    print("\033c")
    game_code = input("Welcome to Heads Up Poker! Please enter your game code, or press enter to start a new game: ")
    if game_code == "":
        game_code = send_message("new_game", s)
        print("Your Public Game Code is: " + game_code)
        # game_state = send_message("join_game" + game_code + " 1", s)
        player = 1
        game_state = json.loads(s.recv(BUFFER_SIZE).decode())
    else:
        game_state = json.loads(send_message("join_game " + game_code, s))
        player = 2


    print("\033c")
    while True:
        turn = game_state["turn"]
        if(game_state["status"] == 1):
            # clear terminal
            print("\033c")
        if game_state["status"] == 3:
            print("\033c")
            print("Game Over!")
            print(game_state["comment"])
            send_message("close", s)
    
        if len(game_state['comment']) > 0:
            print(game_state["comment"] )

        print("Your hand is: ")
        print_deck(game_state["player_" + str(player) + "_hand"])
        print("Your balance is: " + str(game_state["player_" + str(player) + "_balance"]))
        print("Your blind is: " + str(game_state["player_" + str(player) + "_blind"]))
        print("Your opponent's balance is: " + str(game_state["player_" + str(3 - player) + "_balance"]))
        print("Your opponent's blind is: " + str(game_state["player_" + str(3 - player) + "_blind"]))
        print("The pot is: " + str(game_state["pot_balance"]))
        # print("The cards on the table are: " + str(game_state["throw_down_cards"]))
        print("The cards on the table are: " )
        print_deck(game_state["throw_down_cards"])

        if turn == player:
            print("You are up")
            # print("Your hand is: " + str(game_state["player_" + str(player) + "_hand"]))
            
            allowed_options = ["check(c)", "bet(b)", "fold(f)"]
            if game_state["pending_bet"] > 0:
                print("The pending bet is: " + str(game_state["pending_bet"]))
                allowed_options = ["call(a) opponents bet of " + str(game_state["pending_bet"]), "raise(r)", "fold(f)"]
            print("\n\n Your options are: " + str(allowed_options))
            action = input("\n\nPlease enter your action: ")
            if game_state["pending_bet"] > 0:
                while action not in ["a", "r", "f"]:
                    action = input(str(action) + " is not a valid option. Please enter your action: ")
            else:
                while action not in [ "b", "c", "f"]:
                    action = input(str(action) + " is not a valid option. Please enter your action: ")

            game_state = json.loads(handle_action(action, s, game_state, player))
        else:
            print("Player " + str(turn) + " is up\n")
            game_state = json.loads(s.recv(BUFFER_SIZE).decode())


