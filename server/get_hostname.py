import socket

ip_address = socket.gethostbyname(socket.gethostname())
print(f"My IP Address: {ip_address}")
