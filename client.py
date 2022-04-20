# client.py
import asyncio
import websockets

# handle game logic
async def game_loop():
    # server address
    uri = 'ws://localhost:8765'
    # connect to server
    async with websockets.connect(uri) as websocket:
        print("Lets play a guessing game! \n Guess a number between 1 and 100")
        guess = 0

        try:
            while True:
                # get guess from client
                guess = int(input("Your guess: "))
                # send guess to server
                await websocket.send(str(guess))
                # get response from server
                response = await websocket.recv()
                # print response
                print("RESPONSE: {}".format(response))
        except Exception as e:
            print("Error: {}".format(e))


asyncio.get_event_loop().run_until_complete(game_loop())
