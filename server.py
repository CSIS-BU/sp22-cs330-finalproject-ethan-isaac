# server.py
import random
import asyncio
import websockets

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

# create new game
def create_new_game():
    # create deck
    deck = create_fresh_deck()
    # shuffle deck
    deck = shuffle_deck(deck)
    # return deck
    return deck

deck = create_new_game()
print_deck(deck)

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