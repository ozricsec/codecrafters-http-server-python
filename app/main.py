import socket  # noqa: F401
import asyncio
import sys
from pathlib import Path

HOST = "localhost"
PORT = 4221


def handle_root(writer: asyncio.StreamWriter) -> None:
    writer.write(b"HTTP/1.1 200 OK\r\n\r\n")


def handle_echo(path: str, writer: asyncio.StreamWriter) -> None:
    body = path.split("/")[-1]
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
        b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" +
        body.encode()
    )
    writer.write(response)


def handle_user_agent(headers: list[str], writer: asyncio.StreamWriter) -> None:
    ua = headers[2][12:]
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
        b"Content-Length: " + str(len(ua)).encode() + b"\r\n\r\n" +
        ua.encode()
    )
    writer.write(response)
    
    
def handle_files(filename: str, writer: asyncio.StreamWriter) -> None:
    file_path = Path(sys.argv[2]) / filename

    with open(file_path, "rb") as f:
        content = f.read()

    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/octet-stream\r\n"
        b"Content-Length: " + str(len(content)).encode() + b"\r\n\r\n" +
        content
    )
    writer.write(response)
        
            


def handle_404(writer: asyncio.StreamWriter) -> None:
    writer.write(b"HTTP/1.1 404 Not Found\r\n\r\n")


async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        byte_data = await reader.read(4096)
        data = byte_data.decode("utf-8")

        if not data:
            writer.close()
            await writer.wait_closed()
            return

        path = data.split(" ")[1]
        headers = data.split("\r\n")

        # Routing
        if path == "/":
            handle_root(writer)
        elif path.split("/")[1] == "echo":
            handle_echo(path, writer)
        elif path.split("/")[1] == "user-agent":
            handle_user_agent(headers, writer)
        elif path.split("/")[1] == "files":
            file_path = Path(sys.argv[2]) / path.split("/")[2]
            handle_files(path.split("/")[2], writer) if file_path.exists() else handle_404(writer)
        else:
            handle_404(writer)

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