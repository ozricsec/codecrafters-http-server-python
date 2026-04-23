import socket  # noqa: F401
import asyncio

HOST = "localhost"
PORT = 4221


async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        byte_data = await reader.read(4096)
        data = byte_data.decode("utf-8")
        if not data:
            break
        path = data.split(" ")[1]
        headers = data.split("\r\n")
        if path == "/":
            writer.write(b"HTTP/1.1 200 OK\r\n\r\n")
        elif path.split("/")[1] == "echo":
            body = path.split("/")[-1]
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: " + str(len(body)).encode() +b"\r\n\r\n" + body.encode())
        elif path.split("/")[1] == "user-agent":
            ua = headers[2][12:]
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: " + str(len(ua)).encode() + b"\r\n\r\n" + ua.encode())
        else:
            writer.write(b"HTTP/1.1 404 Not Found\r\n\r\n")
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
