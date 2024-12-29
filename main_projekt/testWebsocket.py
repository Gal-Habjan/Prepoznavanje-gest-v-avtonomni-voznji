import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        await websocket.send(f"Echo: {message}")

async def main():
    start_server = websockets.serve(echo, "localhost", 8765)
    await start_server

    await asyncio.Future()  # Keeps the server running

asyncio.run(main())