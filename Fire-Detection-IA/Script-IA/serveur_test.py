import asyncio
import websockets

# Note : on a retiré le paramètre "path" qui n'est plus requis dans les nouvelles versions
async def reception_alertes(websocket):
    print(" [SERVEUR] La Jetson est connectée !")
    try:
        async for message in websocket:
            print(f" [ALERTE REÇUE] -> {message}")
    except websockets.exceptions.ConnectionClosed:
        print(" [SERVEUR] Déconnexion.")

async def main():
    print(" Faux Serveur en écoute sur le port 8765... En attente du feu...")
    # L'instruction 'async with' gère proprement l'ouverture et la fermeture du serveur
    async with websockets.serve(reception_alertes, "127.0.0.1", 8765):
        await asyncio.Future()  # Fait tourner le serveur à l'infini

if __name__ == "__main__":
    # C'est la nouvelle méthode standard (Python 3.7+) pour lancer un programme asynchrone
    asyncio.run(main())
