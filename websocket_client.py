import asyncio
import websockets

async def client_task(client_id):
    uri = "ws://localhost:6969"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Client {client_id} connected")
            while True:
                try:
                    # Send a message
                    message = f"receiver={client_id}|identity={client_id}|Hello from client {client_id}!"
                    await websocket.send(message)
                    print(f"Client {client_id} sent: {message}")

                    # Receive response
                    response = await websocket.recv()
                    print(f"Client {client_id} received: {response}")

                    # Wait before sending the next message
                    await asyncio.sleep(5)
                except websockets.ConnectionClosed:
                    print(f"Client {client_id} disconnected by server")
                    break
                except Exception as e:
                    print(f"Client {client_id} error: {e}")
                    break
    except Exception as e:
        print(f"Client {client_id} failed to connect: {e}")

    # Cleanup
    print(f"Closing client {client_id}")

async def main():
    num_clients = 5
    tasks = []

    # Create and start all clients
    for i in range(num_clients):
        # Start a task for each client
        task = asyncio.create_task(client_task(i))
        tasks.append(task)
        await asyncio.sleep(0.1)  # Small delay to stagger connections

    # Wait for all tasks to complete
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())