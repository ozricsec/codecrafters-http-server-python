import socket  # noqa: F401


def main():
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client, _ = server_socket.accept()
        
        data = client.recv(4096).decode("utf-8")
        print(data.split(" "))
        path = data.split(" ")[1]
        print(path.split("/"))
        
        if path == "/":
            client.send("HTTP/1.1 200 OK\r\n\r\n".encode())
        if path.split("/")[0] == "echo":
            body = path.split("/")[-1]
            client.send(f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {body} \r\n\r\n".encode())
        else:
            client.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
    


if __name__ == "__main__":
    main()
