# importing socket library
import socket

# creating socket defult settings are ipv4 and TCP/IP protocol
s = socket.socket()
print("Socket has been created")

# assaiging ip and port adress for the socket
s.bind(("localhost", 9992))
print("Waiting for connection")

# setting number of client which it can listen
s.listen(1)

# running server
# recivceving client connection
client, addrs = s.accept()

print("Succesfully connected with:{0}".format(addrs))
fileName = client.recv(1024).decode("utf-8")

if fileName == "myFile.txt":
    f = open(fileName)
    content = f.read()
    client.send(bytes(content, "utf-8"))
else:
    client.send(bytes("File is not available", "utf-8"))

# clossing the connection
s.close()
