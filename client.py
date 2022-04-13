# client.py
import asyncio
import websockets

async def hello():
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as websocket:
        name = input("What's your name?")

        await websocket.send(name)

        response = await websocket.recv()
        print(f"<{response}")