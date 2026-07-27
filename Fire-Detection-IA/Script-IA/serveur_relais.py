import asyncio
import websockets

# This list will keep track of all connected dashboards
clients_connectes = set()

async def relais_alertes(websocket):
    print(f"[SERVER] New network connection detected")
    clients_connectes.add(websocket)
    try:
        async for message in websocket:
            print(f"[MESSAGE RECEIVED FROM THE AI] -> {message}")
            
            for client in clients_connectes:
                if client != websocket:
                    try:
                        await client.send(message)
                    except:
                        pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        print("[SERVER] A device has disconnected")
        clients_connectes.remove(websocket)

async def main():
    print("Relay server listening on port 8765...")
    async with websockets.serve(relais_alertes, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())