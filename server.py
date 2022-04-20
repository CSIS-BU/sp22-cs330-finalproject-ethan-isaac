# server.py
import random
import asyncio
import websockets

# texas hold'em hand rankings
RANKINGS = { "High Card": 0, "Pair": 1, "Two Pair": 2, "Three of a Kind": 3, "Straight": 4, "Flush": 5, "Full House": 6, "Four of a Kind": 7, "Straight Flush": 8, "Royal Flush": 9 }

# card suits
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

# royal cards
ROYAL = ["Jack", "Queen", "King", "Ace"]

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


# create new game and return starting game state
def create_new_game(player1, player2):
    # create deck
    deck = create_fresh_deck()
    # shuffle deck
    deck = shuffle_deck(deck)
    # return starting game state
    return {
        "player_1" : player1,
        "player_2" : player2,
        "player_1_balance": 20,
        "player_2_balance": 20,
        "player_1_hand" : [],
        "player_2_hand": [],
        "player_1_blind": 2,
        "player_2_blind": 1,
        "throw_down_cards": [],
        "pot_balance": 0,
        "deck": deck
        }

games = {
    "game_key": create_new_game("IP1", "IP2")
}
print(games['game_key'])

# server 
# async def run_server(websocket, path): 
#     # generate random number between 1 and 100
#     answer = int(100 * (random.random())) + 1
#     # get websocket id
#     guess = await websocket.recv()
#     print("Received: {}".format(guess))
#     if(answer == int(guess)):
#         await websocket.send("You got it!")
#     else:
#         await websocket.send("Try again!")


# start_server = websockets.serve(run_server, "localhost", 8765)

# # start server
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()