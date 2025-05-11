import asyncio
import socket

async def create_client(client_id):
    # Create and connect an asyncio client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect(("localhost", 6969))
        client_socket.setblocking(False)
        print(f"Client {client_id} connected")
        return client_socket
    except Exception as e:
        print(f"Client {client_id} failed to connect: {e}")
        client_socket.close()
        raise

async def client_task(client_id, client_socket):
    loop = asyncio.get_running_loop()
    while True:
        try:
            # Send a message
            message = f"identity=gui|Hello from client {client_id}!\n"
            await loop.sock_sendall(client_socket, message.encode("utf-8"))
            print(f"Client {client_id} sent: {message}")

            # Receive response
            data = await loop.sock_recv(client_socket, 1024)
            if data:
                response = data.decode("utf-8")
                print(f"Client {client_id} received: {response}")
            else:
                print(f"Client {client_id} disconnected by server")
                break

            # Wait before sending the next message
            await asyncio.sleep(5)
        except ConnectionError:
            print(f"Client {client_id} connection error")
            break
        except Exception as e:
            print(f"Client {client_id} error: {e}")
            break

    # Cleanup
    print(f"Closing client {client_id}")
    client_socket.close()

async def main():
    num_clients = 5
    tasks = []

    # Create and start all clients
    for i in range(num_clients):
        try:
            client_socket = await create_client(i)
            # Start a task for each client
            task = asyncio.create_task(client_task(i, client_socket))
            tasks.append(task)
            asyncio.sleep(0.1)
        except Exception:
            continue

    # Wait for all tasks to complete (or handle cancellation)
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())