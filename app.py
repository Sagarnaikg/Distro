import socket
import json
print("Hello select the mode")
print("1.Central server")
print("2.Client")
print("3.Worker server")

mode = input("Enter your mode = ")

port_no = 9932

# final user
user = None
# stores the adress of all the work servers
workers_adress = []
# stores the object of all the work servers
workers_conec = []

# creating socket defult settings are ipv4 and TCP/IP protocol
s = socket.socket()


############################## CENTRAL SERVER ########################################

def find(n, s):
    l = []
    for i in range(n):
        a = ((s/n)*i)+1
        b = (s/n)*(i+1)
        l.append([int(a), int(b)])
    return l


def server():
    # assaiging ip and port adress for the socket
    s.bind(("localhost", port_no))
    print("Server is ready to connect")
    # setting number of client which it can listen
    s.listen(5)
    # running server
    # recivceving workers server connections
    if len(workers_adress) == 0:
        no = int(input("Enter a no of worker server = "))
        for i in range(no):
            print("{0} server left to setup".format(no-i))
            client, addrs = s.accept()
            workers_adress.append(addrs)
            workers_conec.append(client)
        for addrs in workers_adress:
            print("{0}-{1}".format(addrs[0], addrs[1]))

    # check for busy server
    if len(workers_adress) != 0:
        print("All servers are ready")
    # accept end user connection request
    user, addrs = s.accept()
    while True:
        print("Waiting for a task form client")
        # sending confirmation msg to client
        user.send(bytes("Ready to accept task", "utf-8"))
        msg = user.recv(1024).decode("utf-8")

        if "sum of" in msg:
            num = msg.split(" ")
            num = int(num[2])
            l = find(len(workers_conec), num)
            osum = 0
            for i in range(len(workers_conec)):
                workers_conec[i].send(bytes(json.dumps(l[i]), "utf-8"))
                w_sum = workers_conec[i].recv(1024).decode("utf-8")
                osum = osum+int(w_sum)
            user.send(bytes("Sum = {0}".format(osum), "utf-8"))

        elif msg == "close":
            for clt in workers_conec:
                clt.send(bytes("close", "utf-8"))
            user.send(bytes("close", "utf-8"))
            s.close()
            break
        else:
            for clt in workers_conec:
                clt.send(bytes(msg, "utf-8"))
                clt.send(bytes(msg, "utf-8"))

    """ fileName = client.recv(1024).decode("utf-8") """

    # clossing the connection
    s.close()

################################ CLIENT ######################################


def client():
    # connecting to the server
    s.connect(("localhost", port_no))
    """ s.send(bytes("myFile.txt", "utf-8")) """
    while True:
        try:
            msg = s.recv(1024).decode("utf-8")
            cmd = input("Enter your task = ")
            s.send(bytes(cmd, "utf-8"))
            result = s.recv(1024).decode("utf-8")
            if msg == "close" or cmd == "close":
                break
                s.close()
            else:
                print(result)
                print(msg)
        except:
            print("Error")
            s.close()
            break

    s.close()
############################### WORKER SERVER ###############################


def find_sum(l):
    range_sum = 0

    for i in range(l[0], l[1]+1):
        range_sum = range_sum+i

    return str(range_sum)


def worker():
    # connecting to the server
    s.connect(("localhost", port_no))
    """ s.send(bytes("myFile.txt", "utf-8")) """
    while True:
        try:
            msg = s.recv(1024).decode("utf-8")
            if msg == "close":
                break
                s.close()
            else:
                s.send(bytes(find_sum(json.loads(msg)), "utf-8"))
        except Exception as e:
            print(e)
            break
            s.close()

    s.close()

############################### MAIN CLI #####################################


if mode == "cs":
    print("You selected a central server")
    server()
elif mode == "cl":
    print("You selected a client")
    client()
elif mode == "ws":
    print("You selected a worker server")
    worker()
else:
    print("Invalid")

print("Exit")
