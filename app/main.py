import socket  # noqa: F401


def main():
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client, _ = server_socket.accept()
        
        data = client.recv(4096).decode("utf-8")
        path = data.split(" ")[1]
        headers = data.split("\r\n")
        
        if path == "/":
            client.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        if path.split("/")[1] == "echo":
            body = path.split("/")[-1]
            client.send(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode())
        if path.split("/")[1] == "user-agent":
            ua = headers[2][:12]
            print(ua)
            client.send(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(ua)}\r\n\r\n{ua}".encode())
        else:
            client.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
    


if __name__ == "__main__":
    main()
