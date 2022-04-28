# How to Run Simple Heads Up Texas Hold'em Client and Server

## Required Dependencies / Environment Setup

### Python 3 Installation

If python3 is not already installed and setup, do so through the following link: https://www.python.org/downloads/

## Running the Server

In a terminal window, with python3 installed run the following:

If python installation as 'python'

    python ./server.py

If python installation as 'python3'

    python3 ./server.py

## Running the Client(s)

In order to start a client open a new terminal window with python installed and run the following:

If python installation as 'python'

    python ./client.py

If python installation as 'python3'

    python3 ./client.py

## The Game

This program is a Heads Up Texas Hold'em like card game with a few exceptions:

1. In the event a player folds during a betting or raising round, the previously posted bets do not enter the pot. Bets will only enter the pot if a bet is posted and the opposing player calls it.
2. Blinds do not change and there is no big / small blind, the bind will always be 2 chips.
3. Blinds are automatically placed. For sake of simplicity both players are called in on every hand, meaning the start of each hand they will both have their 2 chip blind already placed in the pot.
4. All pairs are equal, secondary high pair evaluation

### How to start the game

With the server and 2 clients running, pressing enter on the first client will generate a 4 digit game code.
In the second client window type in that game code and press enter. Once you do this the game will start with the second terminal going first.

The prompt on the second clients window will show all the game information and provide the available actions in the game.
