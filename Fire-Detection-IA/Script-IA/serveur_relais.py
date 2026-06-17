import asyncio
import websockets

# Cette liste va garder en mémoire tous les Dashboards connectés
clients_connectes = set()

async def relais_alertes(websocket):
    print(f"🟢 [SERVEUR] Nouvelle connexion réseau détectée !")
    clients_connectes.add(websocket)
    try:
        async for message in websocket:
            print(f"📩 [MESSAGE REÇU DE L'IA] -> {message}")
            
            # Le serveur agit comme un mégaphone : il répète le message à tous les Dashboards (ton PC)
            for client in clients_connectes:
                if client != websocket: # On ne renvoie pas le message à l'IA elle-même
                    try:
                        await client.send(message)
                    except:
                        pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        print("🔴 [SERVEUR] Un appareil s'est déconnecté.")
        clients_connectes.remove(websocket)

async def main():
    # L'adresse "0.0.0.0" est magique : elle dit d'accepter les connexions de n'importe quel PC sur le Wi-Fi
    print("📡 Serveur Relais en écoute sur le port 8765... Prêt à faire le pont !")
    async with websockets.serve(relais_alertes, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())