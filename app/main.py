import socket  # noqa: F401
import asyncio

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


def handle_not_found(writer: asyncio.StreamWriter) -> None:
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
        else:
            handle_not_found(writer)

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