import socket  # noqa: F401
import asyncio

HOST = "localhost"
PORT = 4221


async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            path = data.split(b" ")[1]
            headers = data.split(b"\r\n")
            if path == "/":
                await writer.write(b"HTTP/1.1 200 OK\r\n\r\n")
            if path.split(b"/")[1] == "echo":
                body = path.split(b"/")[-1]
                await writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: %s\r\n\r\n%s" % (len(body), body))
            if path.split(b"/")[1] == "user-agent":
                ua = headers[2][12:]
                await writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: %s\r\n\r\n%s" % (len(ua), ua))
            else:
                await writer.write(b"HTTP/1.1 404 Not Found\r\n\r\n")
            await writer.drain()
    except (asyncio.IncompleteReadError, ConnectionResetError):
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        client_handler,
        HOST,
        PORT,
        family=socket.AF_INET
    )
        
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
