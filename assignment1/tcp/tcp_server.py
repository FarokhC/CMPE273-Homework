import socket
import asyncio

TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024

async def client_handler(reader, writer):
    data = await reader.read(BUFFER_SIZE)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print(f"Received {message!r} from {addr!r}")
    print(f"Send: {message!r}")
    writer.write("pong".encode())
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(client_handler, TCP_IP, TCP_PORT)
    async with server:
        await server.serve_forever()

asyncio.run(main())
