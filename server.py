# server.py
import random
import socket
import threading
import json

# server setup
HOST = "127.0.0.1"
PORT = 8088  
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

# check for pair of cards across sorted hand
def check_for_pair(hand):
    for i in range(len(hand) - 1):
        if hand[i][1] == hand[i+1][1]:
            return (hand[i][1], hand[i+1][1])
    return False

# check for two separate pairs of cards across sorted hand
def check_for_two_pairs(hand):
    first_pair = check_for_pair(hand)
    if first_pair:
        second_pair = check_for_pair(list(filter(lambda x: x[1] not in first_pair, hand)))
        if second_pair:
            return (first_pair, second_pair)
    return False

# check for three of a kind across sorted hand
def check_for_three_of_a_kind(hand):
    for i in range(len(hand) - 2):
        if hand[i][1] == hand[i+1][1] == hand[i+2][1]:
            return (hand[i][1], hand[i+1][1], hand[i+2][1])
    return False

# check for full house across sorted hand
def check_for_full_house(hand):
    three_of_a_kind = check_for_three_of_a_kind(hand)
    if three_of_a_kind:
        pair = check_for_pair(list(filter(lambda x: x[1] not in three_of_a_kind, hand)))
        if pair:
            return (three_of_a_kind, pair) 
    return False

# check for four of a kind across sorted hand
def check_for_four_of_a_kind(hand):
    for i in range(len(hand) - 3):
        if hand[i][1] == hand[i+1][1] == hand[i+2][1] == hand[i+3][1]:
            return (hand[i][1], hand[i+1][1], hand[i+2][1], hand[i+3][1])
    return False

# check for straight across all sorted hand
def check_for_straight(hand):
    in_a_row = []
    for i in range(1, len(hand)):
        if hand[i][1] == hand[i-1][1] + 1:
            in_a_row.append(hand[i][1])
        else:
            in_a_row = []
    return in_a_row if len(in_a_row) == 4 else False

# check for flush across sorted hand
def check_for_flush(hand):
    in_a_row = []
    for i in range(len(hand) - 1):
        if hand[i][0] == hand[i+1][0]:
            in_a_row.append(hand[i][1])
        else:
            in_a_row = []
    return in_a_row if len(in_a_row) == 4 else False

# check for royal flush across sorted hand
def check_for_royal_flush(hand):
    flush = check_for_flush(hand)
    return flush if flush == [1, 10, 11, 12, 13] else False

# check for straight flush across sorted hand
def check_for_straight_flush(hand):
    flush = check_for_flush(hand)
    if flush:
        if check_for_straight(list(map(lambda x: (0, x), flush))):
            return flush
    return False

def evaluate_hand(hand):
    print("Evaluating hand: ", hand)
    print_deck(hand)
    # check for royal flush
    if check_for_royal_flush(hand):
        return "Royal Flush"
    # check for straight flush
    elif check_for_straight_flush(hand):
        return "Straight Flush"
    # check for four of a kind
    elif check_for_four_of_a_kind(hand):
        return "Four of a Kind"
    # check for full house
    elif check_for_full_house(hand):
        return "Full House"
    # check for flush
    elif check_for_flush(hand):
        return "Flush"
    # check for straight
    elif check_for_straight(hand):
        return "Straight"
    # check for three of a kind
    elif check_for_three_of_a_kind(hand):
        return "Three of a Kind"
    # check for two pairs
    elif check_for_two_pairs(hand):
        return "Two Pair"
    # check for pair
    elif check_for_pair(hand):
        return "Pair"

    return "High Card"

# evaluate hand
def evaluate_possible_hands(cards):
    # sort hand
    # sort hand by card value
    cards.sort(key=lambda x: x[1])
    possible_hands = [
        cards[0:5],
        cards[1:6],
        cards[2:7],
    ]
    hand_result, hand_rank = "", 0
    for hand in possible_hands:
        result = evaluate_hand(hand)
        print("EVAL", result)
        rank = RANKINGS[result]
        if(rank >= hand_rank):
            hand_result, hand_rank = result, rank

    return hand_result, hand_rank

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
        "player_2_blind": 2,
        "throw_down_cards": [],
        "pot_balance": 0,
        "deck": deck,
        "pending_bet": 0,
        "last_to_bet": 1,
        "comment": "",
        "status": 0
        }

# reset game state for new round
def reset_game_state(game_state):
    # reset game state
    game_state["turn"] = 2
    game_state["player_1_hand"] = []
    game_state["player_2_hand"] = []
    game_state["throw_down_cards"] = []
    game_state["pot_balance"] = 0
    game_state["pending_bet"] = 0
    game_state["comment"] = ""
    game_state["state"] = 0
    game_state["last_to_bet"] = 2
    deck = create_fresh_deck()
    game_state["deck"] = shuffle_deck(deck)
    # return game state
    return game_state

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
            "comment" : comment,
            "status": game_state["status"]
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
            "comment" : comment,
            "status": game_state["status"]
            }

def send_message_to_addr(addr, message):
    conn = connections[addr]
    conn.sendall(message.encode())

def send_game_state_to_players(code, comment = ""):

    send_message_to_addr(games[code]["player_1"], json.dumps(get_public_game_state(games[code], 1, comment)))
    send_message_to_addr(games[code]["player_2"], json.dumps(get_public_game_state(games[code], 2, comment)))

def next_cards(code):
    game_state = games[code]
    # if there are no cards on the table deal the flop
    if len(game_state["throw_down_cards"]) == 0:
        # burn a card
        game_state["deck"].pop(0)
        # deal cards to table
        game_state["throw_down_cards"].append(game_state["deck"].pop())
        game_state["throw_down_cards"].append(game_state["deck"].pop())
        game_state["throw_down_cards"].append(game_state["deck"].pop())
        # send game state to players
        send_game_state_to_players(code, "")
    # if there are three cards on the table deal the turn
    elif len(game_state["throw_down_cards"]) == 3:
        # burn a card
        game_state["deck"].pop(0)
        # deal cards to table
        game_state["throw_down_cards"].append(game_state["deck"].pop())
        # send game state to players
        send_game_state_to_players(code, "")
    # if there are four cards on the table deal the river
    elif len(game_state["throw_down_cards"]) == 4:
        # burn a card
        game_state["deck"].pop(0)
        # deal cards to table
        game_state["throw_down_cards"].append(game_state["deck"].pop())
        # send game state to players
        send_game_state_to_players(code, "")
    # if there are five cards on the table end the game
    elif len(game_state["throw_down_cards"]) == 5:
        # evaluate possible hands
        player_1_hand = evaluate_possible_hands(game_state["player_1_hand"] + game_state["throw_down_cards"])
        player_2_hand = evaluate_possible_hands(game_state["player_2_hand"] + game_state["throw_down_cards"])
        print("RESULTS", player_1_hand, player_2_hand)
        comment = "Player 1: " + player_1_hand[0] + " || Player 2: " + player_2_hand[0]
        balance = game_state["pot_balance"]
        reset_game_state(games[code])
        deal_cards(games[code])
        if(player_1_hand[1] > player_2_hand[1]):
            game_state["player_1_balance"] += balance
            winner = "Player 1 Wins Hand"
        elif(player_2_hand[1] > player_1_hand[1]):
            game_state["player_2_balance"] += balance
            winner = "Player 2 Wins Hand"
        else:
            game_state["player_1_balance"] += int(balance / 2)
            games[code]["player_2_balance"] += int(balance / 2)
            winner = "Tie Hand"
        
        print("\n\n\nWinner: ", winner, "\nPlayer_1 Eval: ", player_1_hand, "\nPlayer_2_Eval:", player_2_hand, "\n\n\n")
        print("Player 1 Balance: ", game_state["player_1_balance"], "\nPlayer 2 Balance: ", game_state["player_2_balance"], "\nTypes: ", type(game_state["player_1_balance"]), type(game_state["player_2_balance"]))
        print("Pot Balance: ", game_state["pot_balance"], "Type: ", type(game_state["pot_balance"]))
        print("HALF", int(game_state["pot_balance"]) / 2)

        if(game_state["player_1_balance"] <= 0):
            winner = "Player 2 Wins with " + str(game_state["player_2_balance"] + 2) + " Chips"
            game_state["status"] = 3
        elif(game_state["player_2_balance"] <= 0):
            winner = "Player 1 Wins with " + str(game_state["player_1_balance"] + 2) + " Chips"
            game_state["status"] = 3
        
        games[code] = game_state
        comment += "\n" + winner
        send_game_state_to_players(code, comment)

def handle_action(message, player):
    if(message == "new_game"):
        # generate unused game code
        code = random.randint(1000, 9999)
        while code in games:
            code = random.randint(1000, 9999)

        games[str(code)] = create_new_game(player)
        return str(code) # use current timestamp as game id
    elif message[0:9] == "join_game":
        code = message[10:]
        games[code]["player_2"] = player
        # deal cards
        games[code] = deal_cards(games[code])
        send_message_to_addr(player, json.dumps(get_public_game_state(games[code], 2)))
        send_message_to_addr(games[code]["player_1"], json.dumps(get_public_game_state(games[code], 1)))
        return ""
    
    msg = ""
    code = ""
    if(len(message) > 4):
        code = message[:4]
        msg = message[5:]

    print("CODE", code, "MSG |" + msg + "|")

    
    comment = ""
    # preemptively change turn
    current_turn = games[code]["turn"]
    games[code]["status"] = 1
    games[code]["turn"] = 1 if current_turn == 2 else 2
    if msg == "check":
        comment = "Player " + str(current_turn) + " checked"
    elif "bet" in msg:
        amount = int(msg[4:])
        # games[code]["player_" + str(current_turn) + "_balance"] -= amount
        # games[code]["pot_balance"] += amount
        games[code]["pending_bet"] = amount
        games[code]["last_to_bet"] = current_turn
        comment = "Player " + str(current_turn) + " bet " + str(amount)
    elif msg == "call":
        amount = games[code]["pending_bet"]
        games[code]["player_1_balance"] -= amount
        games[code]["player_2_balance"] -= amount
        if games[code]["player_" + str(current_turn) + "_balance"] <= 0:
            games[code]["pot_balance"] += games[code]["player_" + str(current_turn) + "_balance"]
            games[code]["player_" + str(current_turn) + "_balance"] = 0
        games[code]["pot_balance"] +=  (amount * 2)
        games[code]["pending_bet"] = 0
        comment = "Player " + str(current_turn) + " called " + str(amount)
    elif "raise" in msg:
        amount = int(msg[6:])
        # games[code]["player_" + str(current_turn) + "_balance"] -= games[code]["pot_balance"] + amount
        # games[code]["pot_balance"] += amount
        games[code]["pending_bet"] = games[code]["pending_bet"] + amount
        comment = "Player " + str(current_turn) + " raised " + str(amount)
        games[code]["last_to_bet"] = current_turn
        print("RAISED TO", games[code]["pending_bet"])
    elif msg == "fold":
        games[code]["player_" + str(3 - current_turn) + "_balance"] += games[code]["pot_balance"]
        # reset game state
        reset_game_state(games[code])
        deal_cards(games[code])  
        send_game_state_to_players(code, comment)
        return 

    if games[code]["pending_bet"] > 0:
        if(current_turn != games[code]["last_to_bet"]):
            next_cards(code)   
        else:
            send_game_state_to_players(code, comment)
    elif(current_turn != 2):
        next_cards(code)
    else:
        send_game_state_to_players(code, comment)

    return ""

def handle_current_connection(conn, addr):
    while True:
        # receive data
        data = conn.recv(BUFFER_SIZE).decode()
        # if not data:
        #     continue
        if data == "close":
            print("Connection from {} closed".format(addr))
            # remove connection from selector
            connections.pop(addr)
        else:
            # process data
            print("Received data from {}: {}".format(addr, data))
            res = handle_action(data, addr)
            if res and len(res) > 0:
                send_message_to_addr(addr, res)


# create a TCP/IP socket server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind socket
sock.bind((HOST, PORT))
# listen for incoming connections
sock.listen(10)

# clear terminal
print("\033c")
print("Listening on port " + str(PORT))
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