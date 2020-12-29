# importing socket library
import socket

# creating socket
s = socket.socket()

# connecting to the server
s.connect(("localhost", 9992))

s.send(bytes("myFile.txt", "utf-8"))
print(s.recv(1024).decode("utf-8"))
s.close()
