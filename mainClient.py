import uuid
import Client

MAC_ADDR = hex(uuid.getnode())

if __name__ == "__main__":
    client = Client.Client(MAC_ADDR)
    client.discover()
    client.listen_broadcast()
    client.request()
    