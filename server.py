# server.py
from calendar import c
import random
import socket
import time
import threading
import json

# server setup
HOST = "127.0.0.1"
PORT = 8888  
BUFFER_SIZE = 1024

used_game_codes = []

# texas hold'em hand rankings
RANKINGS = { "High Card": 0, "Pair": 1, "Two Pair": 2, "Three of a Kind": 3, "Straight": 4, "Flush": 5, "Full House": 6, "Four of a Kind": 7, "Straight Flush": 8, "Royal Flush": 9 }

# card suits
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

# royal cards
ROYAL = ["Jack", "Queen", "King", "Ace"]

# state
num_active_games = 0
games =  {}
connections = {}
data_lock = threading.Lock()


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
    print("Shuffled deck of {} cards:".format(len(deck)))
    for card in deck:
        print(get_card_value(card), " of ",get_card_suit(card))

# create card deck
def create_fresh_deck():
    deck = []
    for suit in range(4):
        for rank in range(1, 14):
            deck.append((suit, rank))
    return deck

# shuffle deck
def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

# evaluate hand
def evaluate_hand(hand):
    # sort hand
    hand.sort()
    # check for flush
    if hand[0][0] == hand[1][0] == hand[2][0] == hand[3][0] == hand[4][0]:
        return "Flush"
    # check for straight
    if hand[0][1] == hand[1][1] + 1 == hand[2][1] + 2 == hand[3][1] + 3 == hand[4][1] + 4:
        return "Straight"
    # check for four of a kind
    if hand[0][1] == hand[1][1] == hand[2][1] == hand[3][1]:
        return "Four of a kind"
    # check for full house
    if hand[0][1] == hand[1][1] == hand[2][1] and hand[3][1] == hand[4][1]:
        return "Full house"
    # check for three of a kind
    if hand[0][1] == hand[1][1] == hand[2][1]:
        return "Three of a kind"
    # check for two pair
    if hand[0][1] == hand[1][1] and hand[2][1] == hand[3][1]:
        return "Two pair"
    # check for pair
    if hand[0][1] == hand[1][1]:
        return "Pair"
    # check for high card
    return "High card"

# deal cards to players
def deal_cards(game_state):
    # rotate player blinds
    game_state["player_1_blind"], game_state["player_2_blind"] = game_state["player_2_blind"], game_state["player_1_blind"]

    # take blind from each player and add to pot
    game_state["player_1_balance"] -= game_state["player_1_blind"]
    game_state["player_2_balance"] -= game_state["player_2_blind"]
    game_state["pot_balance"] += game_state["player_1_blind"] + game_state["player_2_blind"]

    # burn a card
    game_state["deck"].pop(0)
    # deal cards to player 1
    game_state["player_1_hand"].append(game_state["deck"].pop())
    game_state["player_2_hand"].append(game_state["deck"].pop())
    # deal cards to player 2
    game_state["player_1_hand"].append(game_state["deck"].pop())
    game_state["player_2_hand"].append(game_state["deck"].pop())
    # return game state
    return game_state

# create new game and return starting game state
def create_new_game(player1):
    # create deck
    deck = create_fresh_deck()
    # shuffle deck
    deck = shuffle_deck(deck)
    # return starting game state
    return {
        "turn": 2,
        "player_1" : player1,
        "player_2" : "",
        "player_1_balance": 20,
        "player_2_balance": 20,
        "player_1_hand" : [],
        "player_2_hand": [],
        "player_1_blind": 2,
        "player_2_blind": 1,
        "throw_down_cards": [],
        "pot_balance": 0,
        "deck": deck,
        "pending_bet": 0,
        "comment": "",
        }

def get_public_game_state(game_state, player, comment = ""):
    if player == 1:
        return {
            "turn": game_state["turn"],
            "player_1" : game_state["player_1"],
            "player_2" : game_state["player_2"],
            "player_1_balance": game_state["player_1_balance"],
            "player_2_balance": game_state["player_2_balance"],
            "player_1_hand" : game_state["player_1_hand"],
            "player_1_blind": game_state["player_1_blind"],
            "player_2_blind": game_state["player_2_blind"],
            "throw_down_cards": game_state["throw_down_cards"],
            "pot_balance": game_state["pot_balance"],
            "pending_bet": game_state["pending_bet"],
            "comment" : comment
            }
    else:
        return {
            "turn": game_state["turn"],
            "player_1" : game_state["player_1"],
            "player_2" : game_state["player_2"],
            "player_1_balance": game_state["player_1_balance"],
            "player_2_balance": game_state["player_2_balance"],
            "player_2_hand": game_state["player_2_hand"],
            "player_1_blind": game_state["player_1_blind"],
            "player_2_blind": game_state["player_2_blind"],
            "throw_down_cards": game_state["throw_down_cards"],
            "pot_balance": game_state["pot_balance"],
            "pending_bet": game_state["pending_bet"],
            "comment" : comment
            }

def send_message_to_addr(addr, message):
    conn = connections[addr]
    conn.sendall(message.encode())

def send_game_state_to_players(code, comment = ""):
    send_message_to_addr(games[code]["player_1"], json.dumps(get_public_game_state(games[code], 1, comment)))
    send_message_to_addr(games[code]["player_2"], json.dumps(get_public_game_state(games[code], 2, comment)))
       

def handle_action(message, player):
    if(message == "new_game"):
        # generate unused game code
        code = random.randint(0, 9999)
        while code in games:
            code = random.randint(0, 9999)
        
        games[code] = create_new_game(player)
        return str(code) # use current timestamp as game id
    elif message[0:9] == "join_game":
        code = message[10:len(message) - 2]
        print("CODE", code)
        games[code]["player_2"] = player
        # deal cards
        games[code] = deal_cards(games[code])
        send_message_to_addr(player, json.dumps(get_public_game_state(games[code], 2)))
        send_message_to_addr(games[code]["player_1"], json.dumps(get_public_game_state(games[code], 1)))
        return ""
    
    msg = ""
    code = ""
    if(len(message) > 17):
        code = message[:18]
        msg = message[18:]

    print("CODE", code, "MSG", msg)

    comment = ""
    # preemptively change turn
    current_turn = games[code]["turn"]
    games[code]["turn"] = 1 if current_turn == 2 else 2
    if msg == "check":
        comment = "Player " + str(current_turn) + " checked"
    elif "bet" in msg:
        amount = int(msg[4:])
        games[code]["player_" + str(current_turn) + "_balance"] -= amount
        games[code]["pot_balance"] += amount
        games[code]["pending_bet"] = int(msg[4:])
        comment = "Player " + str(current_turn) + " bet " + str(amount)
    elif msg == "call":
        amount = games[code]["pending_bet"]
        games[code]["player_" + str(current_turn) + "_balance"] -= amount
        games[code]["pot_balance"] += amount
        games[code]["pending_bet"] = 0
        comment = "Player " + str(current_turn) + " called " + str(amount)
    elif msg == "raise":
        amount = int(msg[4:])
        games[code]["player_" + str(current_turn) + "_balance"] -= amount
        games[code]["pot_balance"] += amount
        games[code]["pending_bet"] = int(msg[4:])
        comment = "Player " + str(current_turn) + " raised " + str(amount)
    elif msg == "fold":
        comment = "Player " + str(current_turn) + " folded "


    send_game_state_to_players(code, comment)

    return ""

def handle_current_connection(conn, addr):
    while True:
        # receive data
        data = conn.recv(BUFFER_SIZE).decode()
        if not data:
            continue
        elif data == "close":
            print("Connection from {} closed".format(addr))
            # remove connection from selector
            connections.pop(addr)
        else:
            # process data
            print("Received data: {} from {}".format(data, addr))
            res = handle_action(data, addr)
            if len(res) > 0:
                send_message_to_addr(addr, res)


# create a TCP/IP socket server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind socket
sock.bind((HOST, PORT))
# listen for incoming connections
sock.listen(10)

while True:
    # accept connection
    conn, addr = sock.accept()
    # add connection to list of connections
    data_lock.acquire()
    connections[addr] = conn
    print("Connection from {}".format(addr))
    data_lock.release()

    # handle current connection
    new_thread = threading.Thread(target=handle_current_connection, args=(conn, addr))
    new_thread.start()