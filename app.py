import socket
print("Hello select the mode")
print("1.Server")
print("2.Client")

mode = input("Enter your mode = ")

# importing socket library

# creating socket defult settings are ipv4 and TCP/IP protocol
s = socket.socket()
print("Socket has been created")

if mode == "server":
    print("You selected a server")
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
    client.send(bytes("Hello client", "utf-8"))
    print(fileName)

    # clossing the connection
    s.close()
elif mode == "client":
    # connecting to the server
    s.connect(("localhost", 9992))

    s.send(bytes("myFile.txt", "utf-8"))
    print(s.recv(1024).decode("utf-8"))
    s.close()
else:
    print("Invalid")

print("Exit")
