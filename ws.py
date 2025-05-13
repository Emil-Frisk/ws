import socket
import asyncio
import re

class CommunicationHub():
    def __init__(self):
        self.socket_server = None
        self.clients = {}

    def extract_identity(self, message):
        match = re.search(r'identity=([^|]*)\|', message)
        if match:
            return match.group(1)
        else:
            return None
        
    def extract_receiver(self, message):
        match = re.search(r'receiver=([^|]*)\|', message)
        if match:
            return match.group(1)
        else:
            return None

    def find_receiver_socket(self):
        pass

    async def create_socket_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.setblocking(False)

        host = "localhost"
        port = 6969

        try:
            server_socket.bind((host, port))
            server_socket.listen(5)
            print(f"Server listening on {host}:{port}")
            self.socket_server = server_socket
        except OSError as e:
            print(f"Failed to bind to {host}:{port}")
            raise
        

    async def wait_for_connection(self):
        loop = asyncio.get_running_loop()
        while True:
            try:
                client_socket, client_address = await loop.sock_accept(self.socket_server)
                print(f"Client {client_address} connected!")
                self.clients[client_socket] = {client_address: client_address, "identity": "unknown"}
                asyncio.create_task(self.manage_client_connection(client_socket, client_address))
            except asyncio.CancelledError:
                print("Stopping connection listener")
                break
            except Exception as e:
                print(f"Error accepting connections {e}")
        

    def disconnect_client(self, client_socket):
        if client_socket in self.clients:
            print(f"cleaning up client {self.clients[client_socket]}")
            client_socket.close()
            del self.clients[client_socket]
                    
    def read_data(self):
        pass

    ### Coroutine that manages clients connections
    ### And updates the hubs client pool state
    async def manage_client_connection(self, client_socket, client_address):
        client_socket.setblocking(False)
        loop = asyncio.get_running_loop()
        while True:
            try:
                data = await loop.sock_recv(client_socket, 1024)

                if data:
                    decoded_data = data.decode("utf-8")

                    ### get possible identity
                    identity = self.extract_identity(decoded_data)
                    if identity:
                        self.clients[client_socket].update({"identity": identity})
                    
                    receiver = self.extract_receiver(decoded_data)
                    if receiver:
                        print(f"receiver: {receiver}")

                    response = "Message received"
                    for client_sock in self.clients.keys():
                        client_identity = self.clients[client_sock]["identity"]
                        if client_identity == "1":
                            await loop.sock_sendall(client_sock, response.encode("utf-8"))

                    # print(f"Received data: {decoded_data}")

                    # response = "Message received"
                    # await loop.sock_sendall(client_socket, response.encode("utf-8"))
                else:
                    print(f"Client: {client_address} disconnected")
                    break
            except socket.timeout:
                print(f"Socket timed out")
                continue
            except ConnectionError:
                print(f"Client {client_address} disconnect unexpectedly")
                break
            except Exception as e:
                print(f"Unexpected error: {e} happened while managin clients {client_address} connection, closing connection...")
                break

        self.disconnect_client(client_socket)

    async def shutdown(self):
        print("Shutting down server...")
        if self.socket_server:
            self.socket_server.close()

        for client_socket in list(self.clients.keys()):
            self.disconnect_client(client_socket)

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
            
        await asyncio.sleep(1)


async def main():
    hub = CommunicationHub()

    try:
        await hub.create_socket_server()
        await hub.wait_for_connection()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        await hub.shutdown()

if __name__ == "__main__":
    asyncio.run(main())