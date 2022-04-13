# server.py
import asyncio
import websockets

# server 
async def run_server(websocket, path): 
    # get websocket id
    name = await websocket.recv()
    print("from client: {}".format(name))

    # send message to client
    await websocket.send("Hello {}!".format(name))


start_server = websockets.serve(run_server, "localhost", 8765)

# start server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()