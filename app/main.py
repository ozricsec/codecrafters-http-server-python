import socket  # noqa: F401
import asyncio
import sys
from pathlib import Path

HOST = "localhost"
PORT = 4221


def parse_request(data: str):
    lines = data.split("\r\n")
    request_line = lines[0]
    method, path, _ = request_line.split(" ")

    headers = {}
    i = 1
    while i < len(lines) and lines[i]:
        key, value = lines[i].split(":", 1)
        headers[key.strip().lower()] = value.strip()
        i += 1

    body = "\r\n".join(lines[i+1:]) if i + 1 < len(lines) else ""

    return method, path, headers, body


def handle_root(writer: asyncio.StreamWriter) -> None:
    writer.write(b"HTTP/1.1 200 OK\r\n\r\n")


def handle_echo(path: str, encoding: bool, writer: asyncio.StreamWriter) -> None:
    body = path.split("/")[-1]
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
    )
    if encoding:
        response += b"Content-Encoding: gzip\r\n"
    response += b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body.encode()
    writer.write(response)


def handle_user_agent(headers: dict, writer: asyncio.StreamWriter) -> None:
    ua = headers.get("user-agent", "")
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


def handle_post_files(filename: str, body: str, writer: asyncio.StreamWriter) -> None:
    file_path = Path(sys.argv[2]) / filename

    with open(file_path, "w") as f:
        f.write(body)

    writer.write(b"HTTP/1.1 201 Created\r\n\r\n")


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

        method, path, headers, body = parse_request(data)

        parts = path.strip("/").split("/")

        # Routing
        if path == "/":
            handle_root(writer)

        elif parts[0] == "echo" and len(parts) > 1:
            if "accept-encoding" in headers:
                if "gzip" in headers["accept-encoding"]:
                    handle_echo(path, True, writer)
                else:
                    handle_echo(path, False, writer)
            else:
                handle_echo(path, False, writer)

        elif parts[0] == "user-agent":
            handle_user_agent(headers, writer)

        elif parts[0] == "files" and len(parts) > 1:
            filename = parts[1]
            file_path = Path(sys.argv[2]) / filename

            if method == "GET":
                if file_path.exists():
                    handle_files(filename, writer)
                else:
                    handle_404(writer)

            elif method == "POST":
                handle_post_files(filename, body, writer)

            else:
                handle_404(writer)

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