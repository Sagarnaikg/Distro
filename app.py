from __future__ import print_function, unicode_literals
import socket
import time
import json
import regex
from halo import Halo
from pprint import pprint
from termcolor import colored
from pyfiglet import figlet_format
from PyInquirer import prompt, Separator
from prompt_toolkit.validation import Validator, ValidationError

#-----------------global vaiables------------------------
port_no = 9982
# stores the adress of all the work servers
workers_adress = []
# stores the object of all the work servers
workers_conec = []
# creating socket defult settings are ipv4 and TCP/IP protocol
s = socket.socket()

# welcome msg
print((colored(figlet_format("D I S T R O"), color="yellow")))

#-------------------- uestions---------------------------
selecting_mode = [
    {
        'type': 'list',
        'name': 'mode',
        'message': 'Select a mode',
        'choices': [
            'Central server',
            'Worker server',
            'Client',
        ]
    },
]

confirm_qus = [
    {
        'type': 'confirm',
        'message': 'Do you want to exit?',
        'name': 'exit',
        'default': False,
    },
]

client_qus = [
    {
        'type': 'input',
        'name': 'task',
        'message': 'Enter your task =',
    },
]


# number validator
class WorkersNoValidator(Validator):
    def validate(self, document):
        ok = regex.match('[0-9]+', document.text)
        if not ok:
            raise ValidationError(message='Please enter a valid number',
                                  cursor_position=len(document.text))


selecting_no_of_ws = [
    {
        'type': 'input',
        'name': 'no_of_ws',
        'message': 'Enter a number of worker server',
        'validate': WorkersNoValidator
    },
]

############################## CENTRAL SERVER ########################################


# initial loading animation
def server_loader():
    spinner = Halo(text='Loading', spinner='dots2', color="yellow")
    spinner.start("Staring a System ...")
    time.sleep(2)
    spinner.succeed('System is ready to connect')
    spinner.stop()


# to devide the s in to eaul parts
def find(n, s):
    l = []
    for i in range(n):
        a = ((s / n) * i) + 1
        b = (s / n) * (i + 1)
        l.append([int(a), int(b)])
    return l


def server():
    # STEP 1: CREATE AND BIND THE SERVER :
    # assaiging ip and port adress for the socket
    s.bind(("localhost", port_no))
    server_loader()
    # setting number of client which it can listen
    s.listen(5)
    # running server

    # STEP 2: CONNECT ALL THE WORKER SERVER :
    # recivceving workers server connections
    if len(workers_adress) == 0:
        no_ws_aws = prompt(selecting_no_of_ws)
        no = int(no_ws_aws["no_of_ws"])
        for i in range(no):
            spinner1 = Halo(text='Loading', spinner='dots2', color="yellow")
            spinner1.start(
                "{0} server left to setup (please connect worker severs) ...".
                format(no - i))
            client, addrs = s.accept()
            workers_adress.append(addrs)
            workers_conec.append(client)
            time.sleep(1)
            spinner1.succeed('Succesfully connected with {0}'.format(addrs[0]))
            spinner1.stop()

        print("---------------------------------")
        print("Connected servers")
        print("No.  IP adress   Port    Status")
        for i in range(len(workers_adress)):

            print("[{0}]  {1}   {2}   Free".format(
                (i + 1), workers_adress[i][0], workers_adress[i][1]))
        print("---------------------------------")

    # STEP 3: CONNECT TO CLIENT :
    # accept end user connection request
    spinner3 = Halo(text='Loading', spinner='dots2')
    spinner3.start("Waiting for client to connect (please connect client) ...")
    user, addrs = s.accept()
    time.sleep(1)
    spinner3.succeed('Succesfully connected with client {0}'.format(addrs[0]))
    spinner3.stop()

    # STEP 4: SERVE CLIENT REQUESTS :
    log = 1
    while True:
        spinner4 = Halo(text='Loading', spinner='arrow3')
        spinner4.start("Waiting for a task from client ...")
        # sending confirmation msg to client
        msg = user.recv(1024).decode("utf-8")

        if "sum of" in msg:
            try:
                num = msg.split(" ")
                num = int(num[2])
                l = find(no, num)
                osum = 0
                for i in range(len(workers_conec)):
                    workers_conec[i].send(bytes(json.dumps(l[i]), "utf-8"))
                    w_sum = workers_conec[i].recv(1024).decode("utf-8")
                    osum = osum + int(w_sum)
                user.send(bytes("Sum = {0}".format(osum), "utf-8"))
                spinner4.warn(
                    "[{0}] : resquest = \'{1}\' : response = \'{2}\'".format(
                        log, msg, osum))
                spinner4.stop()
            except Exception as e:
                spinner4.fail("Fail to connect")

        elif msg == "close":
            for clt in workers_conec:
                clt.send(bytes("close", "utf-8"))
            user.send(bytes("close", "utf-8"))
            spinner4.fail(
                "[{0}] : resquest = \'{1}\' : response = \'{2}\'".format(
                    log, msg, "close"))
            spinner4.stop()
            s.close()
            break

        else:
            for clt in workers_conec:
                clt.send(bytes(msg, "utf-8"))
            user.send(bytes("Invalid task", "utf-8"))
            spinner4.warn(
                "[{0}] : resquest = \'{1}\' : response = \'{2}\'".format(
                    log, msg, "Invalid task"))
            spinner4.stop()
        log += 1
    # clossing the connection
    s.close()


################################ CLIENT ######################################


def client():
    # connecting to the server
    spinner3 = Halo(text='Loading', spinner='dots2', color="yellow")
    spinner3.start("Connecting to central server ...")
    s.connect(("localhost", port_no))
    time.sleep(1)
    spinner3.succeed('Succesfully connected with central server')
    spinner3.stop()

    while True:
        print("---------------------------------")
        try:
            task_aws = prompt(client_qus)
            cmd = task_aws["task"]
            if cmd == "close":
                con_aws = prompt(confirm_qus)
                if con_aws["exit"]:
                    s.send(bytes(cmd, "utf-8"))
                    result = s.recv(1024).decode("utf-8")
                    s.close()
                    print("---------------------------------")
                    break
                else:
                    continue
                print("---------------------------------")
            s.send(bytes(cmd, "utf-8"))
            result = s.recv(1024).decode("utf-8")
            print(result)
        except:
            print("Error")
            s.close()
            break

    s.close()


############################### WORKER SERVER ###############################


# FINDING SUM
def find_sum(l):
    range_sum = 0

    for i in range(l[0], l[1] + 1):
        range_sum = range_sum + i

    return str(range_sum)


def worker():
    # connecting to the server
    s.connect(("localhost", port_no))
    spinner2 = Halo(text='Loading', spinner='dots2', color="yellow")
    spinner2.start("Connecting to central server ...")
    time.sleep(1)
    spinner2.succeed('Succesfully connected with central server')
    spinner2.stop()
    while True:
        try:
            msg = s.recv(1024).decode("utf-8")
            try:
                if msg == "close":
                    break
                    s.close()
                else:
                    s.send(bytes(find_sum(json.loads(msg)), "utf-8"))
            except:
                print(msg)

        except Exception as e:
            print(e)
            break
            s.close()

    s.close()


############################### START #####################################
mode_aws = prompt(selecting_mode)

if mode_aws["mode"] == 'Central server':
    server()
elif mode_aws["mode"] == 'Client':
    client()
elif mode_aws["mode"] == 'Worker server':
    worker()
