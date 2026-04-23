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
			
			path = data.split(" ")[1]
			headers = data.split("\r\n")
			
			if path == "/":
				await writer.write("HTTP/1.1 200 OK\r\n\r\n")
			if path.split("/")[1] == "echo":
				body = path.split("/")[-1]
				await writer.write(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{body}")
			if path.split("/")[1] == "user-agent":
				ua = headers[2][12:]
				await writer.write(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(ua)}\r\n\r\n{ua}")
                
			else:
				await writer.write("HTTP/1.1 404 Not Found\r\n\r\n")
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
